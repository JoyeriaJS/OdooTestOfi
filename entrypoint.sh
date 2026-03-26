#!/bin/sh
set -e

# Si las variables ODOO_ no existen, usa las PG* que Railway inyecta automáticamente
: "${ODOO_DATABASE_HOST:=$PGHOST}"
: "${ODOO_DATABASE_PORT:=$PGPORT}"
: "${ODOO_DATABASE_USER:=$PGUSER}"
: "${ODOO_DATABASE_PASSWORD:=$PGPASSWORD}"
: "${ODOO_DATABASE_NAME:=$PGDATABASE}"

echo "Esperando conexión a PostgreSQL en ${ODOO_DATABASE_HOST}:${ODOO_DATABASE_PORT}..."

# Espera a que la base de datos esté lista
while ! nc -z "${ODOO_DATABASE_HOST}" "${ODOO_DATABASE_PORT}" 2>/dev/null; do
  echo "Base de datos no disponible aún, esperando..."
  sleep 3
done

echo "Base de datos disponible. Iniciando Odoo..."

exec odoo \
  --http-port="${PORT:-8069}" \
  --dev=all \
  --without-demo=True \
  --proxy-mode \
  --db_host="${ODOO_DATABASE_HOST}" \
  --db_port="${ODOO_DATABASE_PORT}" \
  --db_user="${ODOO_DATABASE_USER}" \
  --db_password="${ODOO_DATABASE_PASSWORD}" \
  --database="${ODOO_DATABASE_NAME}" \
  --addons-path="/mnt/custom_addons,/usr/lib/python3/dist-packages/odoo/addons"
  
