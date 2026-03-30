#!/bin/sh
set -e

: "${ODOO_DATABASE_HOST:=$PGHOST}"
: "${ODOO_DATABASE_PORT:=$PGPORT}"
: "${ODOO_DATABASE_USER:=$PGUSER}"
: "${ODOO_DATABASE_PASSWORD:=$PGPASSWORD}"
: "${ODOO_DATABASE_NAME:=$PGDATABASE}"

DATA_DIR="/var/lib/odoo"
FILESTORE="${DATA_DIR}/filestore/${ODOO_DATABASE_NAME}"

echo "Esperando PostgreSQL en ${ODOO_DATABASE_HOST}:${ODOO_DATABASE_PORT}..."

while ! nc -z "${ODOO_DATABASE_HOST}" "${ODOO_DATABASE_PORT}" 2>/dev/null; do
  sleep 2
done

echo "DB lista ✅"

# Crear filestore
mkdir -p "${FILESTORE}"
chown -R odoo:odoo /var/lib/odoo || true

echo "🧹 Limpiando assets corruptos desde Odoo shell..."

odoo shell -d "${ODOO_DATABASE_NAME}" <<EOF
env['ir.attachment'].search([('url', 'like', '/web/assets/')]).unlink()
env['ir.attachment'].search([('name', 'like', '.assets_')]).unlink()
EOF

echo "🔄 Reconstruyendo todos los módulos (assets incluidos)..."

odoo \
  --db_host="${ODOO_DATABASE_HOST}" \
  --db_port="${ODOO_DATABASE_PORT}" \
  --db_user="${ODOO_DATABASE_USER}" \
  --db_password="${ODOO_DATABASE_PASSWORD}" \
  --database="${ODOO_DATABASE_NAME}" \
  -u all \
  --stop-after-init || true

echo "🚀 Iniciando Odoo..."

exec odoo \
  --http-port="${PORT:-8069}" \
  --proxy-mode \
  --db_host="${ODOO_DATABASE_HOST}" \
  --db_port="${ODOO_DATABASE_PORT}" \
  --db_user="${ODOO_DATABASE_USER}" \
  --db_password="${ODOO_DATABASE_PASSWORD}" \
  --database="${ODOO_DATABASE_NAME}" \
  --addons-path="/mnt/custom_addons,/usr/lib/python3/dist-packages/odoo/addons"