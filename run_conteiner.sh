#!/usr/bin/env bash

# Detectar comando docker compose
USE_DOCKER_COMPOSE=0
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
	USE_DOCKER_COMPOSE=1
elif command -v docker-compose >/dev/null 2>&1; then
	USE_DOCKER_COMPOSE=0
else
	echo "No docker compose command found. Aborting."
	exit 1
fi

run_compose() {
	if [ "$USE_DOCKER_COMPOSE" -eq 1 ]; then
		docker compose "$@"
	else
		docker-compose "$@"
	fi
}

echo "Cleaning up previous containers..."
run_compose down 2>/dev/null || true

echo "Building and starting containers..."
run_compose up --build -d

echo "Waiting for PostgreSQL to be ready..."

# --- FIX: BUCLE DE ESPERA INTELIGENTE ---
# En lugar de sleep 5, preguntamos a la DB si ya está lista.
# Esto es vital para VirtualBox y máquinas lentas.
wait_for_postgres() {
    local retries=30
    local count=0
    until docker exec postgres-db-3-final pg_isready -U user > /dev/null 2>&1; do
        count=$((count+1))
        if [ $count -gt $retries ]; then
            echo "Error: PostgreSQL no arrancó a tiempo."
            exit 1
        fi
        echo "Esperando a la base de datos... ($count/$retries)"
        sleep 2
    done
    echo "¡PostgreSQL está listo!"
}

wait_for_postgres
# ----------------------------------------

echo ""
echo "Containers status:"
docker ps --filter "name=django-backend-final" --filter "name=postgres-db-3-final"

# Definimos la ruta explícita al python del venv para evitar errores de path
CMD_PYTHON="/opt/venv/bin/python"

echo ""
echo "Creating migrations..."
docker exec django-backend-final $CMD_PYTHON manage.py makemigrations

echo ""
echo "Running migrations..."
docker exec django-backend-final $CMD_PYTHON manage.py migrate

echo ""
echo "Loading initial data (fixtures)..."
docker exec django-backend-final $CMD_PYTHON manage.py loaddata Website/fixtures/initial_data.json 2>/dev/null || echo "No fixtures found, skipping..."

echo ""
echo "Setting up test data..."
docker exec django-backend-final $CMD_PYTHON setup_test_data.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Available URLs:"
echo "  - Account:       http://localhost:8000/account/"
echo "  - Chat:          http://localhost:8000/chat/"
echo "  - Admin:         http://localhost:8000/admin/"
echo ""
echo "To start the Django server:"
echo "  daphne -b 0.0.0.0 -p 8000 d09.asgi:application"
echo ""

# Abrir shell
docker exec -it django-backend-final /bin/zsh