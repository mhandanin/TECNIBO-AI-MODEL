# Built from the repo root: docker build -f app/Dockerfile .
#
# Installed with `pip install -e` (not a plain install) so that
# pricing_app/config.py, which resolves PROJECT_ROOT via
# Path(__file__).resolve().parents[N], keeps pointing at a coherent path
# once copied into the image (a regular install would move the file into
# site-packages and break that resolution).
FROM python:3.11-slim
WORKDIR /repo

COPY app/ ./app/
RUN pip install --no-cache-dir -e ./app

EXPOSE 8000
CMD ["uvicorn", "pricing_app.main:app", "--app-dir", "app/src", "--host", "0.0.0.0", "--port", "8000"]
