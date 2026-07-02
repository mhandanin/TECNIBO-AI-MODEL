# Built from the repo root: docker build -f api/Dockerfile .
#
# Installed with `pip install -e` (not a plain install) so that
# pricing_api/config.py, which resolves PROJECT_ROOT/API_DIR via
# Path(__file__).resolve().parents[N], keeps pointing at a coherent path
# once copied into the image (a regular install would move the file into
# site-packages and break MODEL_ARTIFACTS_DIR / .env resolution).
FROM python:3.11-slim
WORKDIR /repo

COPY ml/ ./ml/
COPY api/ ./api/
RUN pip install --no-cache-dir -e ./ml -e ./api

EXPOSE 8000
CMD ["uvicorn", "pricing_api.main:app", "--app-dir", "api/src", "--host", "0.0.0.0", "--port", "8000"]
