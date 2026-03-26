#!/bin/sh
set -e

: "${ODOO_DATABASE_HOST:=$PGHOST}"
: "${ODOO_DATABASE_PORT:=$PGPORT}"
: "${ODOO_DATABASE_USER:=$PGUSER}"
: "${ODOO_DATABASE_PASSWORD:=$PGPASSWORD}"
: "${ODOO_DATABASE_NAME:=$PGDATABASE}"

echo "⏳ Esperando PostgreSQL REAL (no solo puerto)..."

# Espera real usando conexión SQL
until PGPASSWORD=$ODOO_DATABASE_PASSWORD psql -h "$ODOO_DATABASE_HOST" -p "$ODOO_DATABASE_PORT" -U "$ODOO_DATABASE_USER" -d "$ODOO_DATABASE_NAME" -c '\q' 2>/dev/null; do
  echo "❌ PostgreSQL no listo aún..."
  sleep 3
done

echo "✅ PostgreSQL listo. Iniciando Odoo..."

exec odoo \
  --http-port="${PORT:-8069}" \
  --without-demo=True \
  --proxy-mode \
  --max-cron-threads=0 \
  --db_host="${ODOO_DATABASE_HOST}" \
  --db_port="${ODOO_DATABASE_PORT}" \
  --db_user="${ODOO_DATABASE_USER}" \
  --db_password="${ODOO_DATABASE_PASSWORD}" \
  --database="${ODOO_DATABASE_NAME}" \
  --db_maxconn=20 \
  --addons-path="/mnt/custom_addons,/usr/lib/python3/dist-packages/odoo/addons"