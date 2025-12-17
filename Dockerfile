FROM ghcr.io/astral-sh/uv:0.9.13 AS uv
FROM python:3.14-slim

COPY --from=uv /uv /uvx /bin/

ARG APP_UID=1000
ARG APP_USER=app
ARG APP_GROUP=app

ADD app.py pyproject.toml README.md uv.lock* yggtorrent_tracker_fixerr /app/
ADD entrypoint.sh /entrypoint.sh
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
 && groupadd -g "${APP_UID}" "${APP_GROUP}" \
 && useradd -m -u "${APP_UID}" -g "${APP_GROUP}" "${APP_USER}" \
 && chmod +x /entrypoint.sh \
 && uv sync --frozen --no-dev \
 && chown -R "${APP_USER}:${APP_GROUP}" /app

USER "${APP_USER}"

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["/entrypoint.sh"]
CMD []
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f "http://127.0.0.1:${LISTEN_PORT:-8000}/healthz" || exit 1
