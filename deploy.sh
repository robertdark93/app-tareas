#!/bin/bash
set -e

REMOTE_USER="hades"
REMOTE_HOST="10.25.1.131"
REMOTE_PASS="Death123*"
REMOTE_DIR="/opt/app_tareas"
PROXY="http://10.25.1.229:3128"

VERDE='\033[0;32m'; AMARILLO='\033[1;33m'; CYAN='\033[0;36m'; ROJO='\033[0;31m'; RESET='\033[0m'
info()  { echo -e "${CYAN}ℹ️${RESET} $1"; }
ok()    { echo -e "${VERDE}✅${RESET} $1"; }
warn()  { echo -e "${AMARILLO}⚠️${RESET} $1"; }

if ! command -v sshpass &>/dev/null; then
    info "Instalando sshpass..."
    sudo http_proxy="$PROXY" https_proxy="$PROXY" apt-get install -y -qq sshpass
fi

info "Empaquetando proyecto..."
TARBALL="/tmp/app_tareas_deploy.tar.gz"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "$SCRIPT_DIR/.env" ]; then
    warn "No hay .env — generando SECRET_KEY automática..."
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    cat > "$SCRIPT_DIR/.env" << EOF
DJANGO_SECRET_KEY=$SECRET
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$REMOTE_HOST,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://$REMOTE_HOST,http://localhost
DB_NAME=tareas
DB_USER=tareas
DB_PASSWORD=tareas
HTTP_PROXY=$PROXY
HTTPS_PROXY=$PROXY
APP_PORT=5000
EOF
    ok ".env creado con SECRET_KEY única"
fi

tar czf "$TARBALL" \
    --exclude=venv --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='*.pyo' --exclude=.git --exclude='db.sqlite3' \
    --exclude=staticfiles --exclude='.DS_Store' \
    -C "$SCRIPT_DIR" .

info "Subiendo a ${REMOTE_USER}@${REMOTE_HOST}..."
sshpass -p "$REMOTE_PASS" scp -o StrictHostKeyChecking=no \
    "$TARBALL" "${REMOTE_USER}@${REMOTE_HOST}:/tmp/app_tareas_deploy.tar.gz"
sshpass -p "$REMOTE_PASS" scp -o StrictHostKeyChecking=no \
    "$SCRIPT_DIR/.env" "${REMOTE_USER}@${REMOTE_HOST}:/tmp/app_tareas.env"
ok "Archivos subidos."

info "Desplegando en ${REMOTE_HOST}..."
sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no \
    -o RequestTTY=yes \
    "${REMOTE_USER}@${REMOTE_HOST}" \
    "REMOTE_PASS='$REMOTE_PASS' REMOTE_DIR='$REMOTE_DIR' PROXY='$PROXY' REMOTE_HOST='$REMOTE_HOST' bash -s" << 'REMOTE_SCRIPT'
set -e

sudox() { echo "$REMOTE_PASS" | sudo -S "$@"; }

echo "🔍 Verificando Docker..."
if ! command -v docker &>/dev/null; then
    echo "🐳 Instalando Docker..."
    export http_proxy="$PROXY" https_proxy="$PROXY"
    curl -fsSL https://get.docker.com | sh
    sudox usermod -aG docker "$USER"
fi

if ! docker compose version &>/dev/null 2>&1; then
    echo "🐳 Instalando docker-compose plugin..."
    sudox apt-get update -qq
    sudox apt-get install -y -qq docker-compose-plugin 2>/dev/null || true
fi

if ! sudo docker info &>/dev/null; then
    echo "🚀 Arrancando Docker..."
    sudox systemctl start docker 2>/dev/null || sudox service docker start 2>/dev/null || true
fi

echo "📂 Preparando $REMOTE_DIR..."
sudox mkdir -p "$REMOTE_DIR"
sudox chown "$USER:$USER" "$REMOTE_DIR"

echo "📦 Extrayendo..."
tar xzf /tmp/app_tareas_deploy.tar.gz -C "$REMOTE_DIR"
rm -f /tmp/app_tareas_deploy.tar.gz
cp /tmp/app_tareas.env "$REMOTE_DIR/.env"
rm -f /tmp/app_tareas.env

cd "$REMOTE_DIR"
mkdir -p media backups

echo "🔍 Verificando puerto..."
if ! ss -tlnp | grep -q ':5000 '; then
    APP_PORT=5000
elif ! ss -tlnp | grep -q ':5001 '; then
    APP_PORT=5001
else
    echo "❌ Puertos 5000 y 5001 ocupados."
    exit 1
fi
echo "✅ Usando puerto $APP_PORT"
DETECTED_PORT=$APP_PORT

set -a; source .env; set +a
export APP_PORT=${DETECTED_PORT:-5000}

echo "🐳 Construyendo y levantando contenedores..."
sudox env APP_PORT="$APP_PORT" HTTP_PROXY="$HTTP_PROXY" HTTPS_PROXY="$HTTPS_PROXY" \
    docker compose up -d --build

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  http://$REMOTE_HOST:$APP_PORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
REMOTE_SCRIPT

rm -f "$TARBALL"
ok "Despliegue completado."
