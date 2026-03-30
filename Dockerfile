FROM odoo:17.0

# 🔥 Forzar rebuild SIEMPRE (evita cache de Railway)
ARG CACHE_BUST=1
RUN echo "Build forced at $(date) - $CACHE_BUST"

ARG LOCALE=en_US.UTF-8
ENV LANGUAGE=${LOCALE}
ENV LC_ALL=${LOCALE}
ENV LANG=${LOCALE}

USER root

# Dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    netcat-openbsd \
    && locale-gen ${LOCALE}

# 🔥 Verificación directa de versión (clave para debug)
RUN odoo --version

WORKDIR /app

# Copiar entrypoint correctamente
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Addons custom
COPY ./custom_addons /mnt/custom_addons

# Usar entrypoint correcto
ENTRYPOINT ["/entrypoint.sh"]