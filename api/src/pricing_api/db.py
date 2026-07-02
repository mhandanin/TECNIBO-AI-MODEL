"""Database access: model runs registry, material/profile lookups, prediction log."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Row

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)


def get_latest_model_run() -> Optional[Row]:
    with engine.begin() as conn:
        return conn.execute(
            text(
                """
                SELECT id_entrainement, nom_modele, version, chemin_artifact,
                       r2, mae, rmse, nb_echantillons, date_entrainement
                FROM modele_entrainement
                ORDER BY date_entrainement DESC
                LIMIT 1
                """
            )
        ).mappings().first()


def list_materiaux() -> list[str]:
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT nom FROM materiau ORDER BY nom")).all()
    return [r[0] for r in rows]


def list_profiles() -> list[str]:
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT nom FROM profile ORDER BY nom")).all()
    return [r[0] for r in rows]


def lookup_materiau_price(nom: str) -> Optional[float]:
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT prix_m2 FROM materiau WHERE nom = :nom"), {"nom": nom}
        ).first()
    return float(row[0]) if row else None


def lookup_profile_price(nom: str) -> Optional[float]:
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT prix_unitaire FROM profile WHERE nom = :nom"), {"nom": nom}
        ).first()
    return float(row[0]) if row else None


def insert_prediction(
    id_entrainement: int,
    largeur_mm: int,
    hauteur_mm: int,
    surface_m2: float,
    materiau_prix_m2: float,
    profile_prix_unitaire: float,
    code_spp: str,
    complexity_factor: float,
    logistics_cost: float,
    prix_predit: float,
    latence_ms: float,
    source: str = "api",
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO prediction (
                    id_entrainement, largeur_mm, hauteur_mm, surface_m2,
                    materiau_prix_m2, profile_prix_unitaire, code_spp,
                    complexity_factor, logistics_cost, prix_predit,
                    latence_ms, source
                ) VALUES (
                    :id_entrainement, :largeur_mm, :hauteur_mm, :surface_m2,
                    :materiau_prix_m2, :profile_prix_unitaire, :code_spp,
                    :complexity_factor, :logistics_cost, :prix_predit,
                    :latence_ms, :source
                )
                """
            ),
            {
                "id_entrainement": id_entrainement,
                "largeur_mm": largeur_mm,
                "hauteur_mm": hauteur_mm,
                "surface_m2": surface_m2,
                "materiau_prix_m2": materiau_prix_m2,
                "profile_prix_unitaire": profile_prix_unitaire,
                "code_spp": code_spp,
                "complexity_factor": complexity_factor,
                "logistics_cost": logistics_cost,
                "prix_predit": prix_predit,
                "latence_ms": latence_ms,
                "source": source,
            },
        )
