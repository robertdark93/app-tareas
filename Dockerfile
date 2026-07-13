FROM python:3.13-slim

ARG http_proxy
ARG https_proxy
ENV http_proxy=$http_proxy https_proxy=$https_proxy

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/* || echo "WARNING: postgresql-client not installed (no network)"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --gid 1001 --no-create-home app && \
    chown -R app:app /app
USER app

RUN chmod +x docker-entrypoint.sh

EXPOSE 5006

ENTRYPOINT ["./docker-entrypoint.sh"]
