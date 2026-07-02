#!/usr/bin/env python3
"""Import the training dataset into PostgreSQL (materiau / profile / article).

Reuses the cleaning logic from the pricing_ml package (same rules as the
model training pipeline) so the database and the model are always built from
the same definition of "valid row".

This script is idempotent: it truncates materiau/profile/article before
reloading them from the source file. It never touches prediction or
modele_entrainement (production history must survive a re-import of the
training data).

Usage:
    python import_dataset.py
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pricing_ml.data import clean_dataframe, load_dataset
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.environ["DATABASE_URL"]


def get_engine():
    return create_engine(DATABASE_URL)


def reset_training_tables(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE article, profile, materiau RESTART IDENTITY CASCADE"))


def import_materiau(engine, df: pd.DataFrame) -> dict[str, int]:
    materiau_df = (
        df[["Material", "Material_price_m2"]]
        .drop_duplicates()
        .rename(columns={"Material": "nom", "Material_price_m2": "prix_m2"})
    )
    materiau_df.to_sql("materiau", engine, if_exists="append", index=False)

    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id_materiau, nom FROM materiau")).all()
    return {nom: id_materiau for id_materiau, nom in rows}


def import_profile(engine, df: pd.DataFrame) -> dict[str, int]:
    profile_df = (
        df[["Profile", "Profile_price_unit"]]
        .drop_duplicates()
        .rename(columns={"Profile": "nom", "Profile_price_unit": "prix_unitaire"})
    )
    profile_df.to_sql("profile", engine, if_exists="append", index=False)

    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id_profile, nom FROM profile")).all()
    return {nom: id_profile for id_profile, nom in rows}


def import_article(engine, df: pd.DataFrame, materiau_ids: dict[str, int], profile_ids: dict[str, int]) -> None:
    article_df = pd.DataFrame(
        {
            "largeur_mm": df["Width_mm"],
            "hauteur_mm": df["Height_mm"],
            "surface_m2": df["Surface_m2"],
            "code_spp": df["SPP"],
            "complexity_factor": df["Complexity_factor"],
            "logistics_cost": df["Logistics_cost"],
            "prix_reel": df["Article_price"],
            "id_materiau": df["Material"].map(materiau_ids),
            "id_profile": df["Profile"].map(profile_ids),
        }
    )
    article_df.to_sql("article", engine, if_exists="append", index=False, chunksize=1000)


def main() -> None:
    df = load_dataset()
    df = clean_dataframe(df)
    print(f"Loaded and cleaned {len(df)} rows")

    engine = get_engine()
    reset_training_tables(engine)

    materiau_ids = import_materiau(engine, df)
    print(f"Imported {len(materiau_ids)} materiaux")

    profile_ids = import_profile(engine, df)
    print(f"Imported {len(profile_ids)} profiles")

    import_article(engine, df, materiau_ids, profile_ids)
    print(f"Imported {len(df)} articles")


if __name__ == "__main__":
    main()
