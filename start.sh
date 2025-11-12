#!/usr/bin/env bash
set -euo pipefail

echo ">>> Installing python dependencies"
pip install -r requirements.txt

echo ">>> Running Alembic migrations"
# Espera que DATABASE_URL esté definido en env vars (Render dashboard)
alembic upgrade head

echo ">>> Build finished"
