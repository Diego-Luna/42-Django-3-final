
#!/usr/bin/env bash

# Detect docker compose command (POSIX-friendly)
USE_DOCKER_COMPOSE=0
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
	USE_DOCKER_COMPOSE=1
elif command -v docker-compose >/dev/null 2>&1; then
	USE_DOCKER_COMPOSE=0
else
	echo "No docker compose command found. Aborting."
	exit 1
fi

# Helper to run compose commands portably
run_compose() {
	if [ "$USE_DOCKER_COMPOSE" -eq 1 ]; then
		docker compose "$@"
	else
		docker-compose "$@"
	fi
}

# Stop any previous containers if they exist
echo "Cleaning up previous containers..."
run_compose down 2>/dev/null || true

# Build and start containers
echo "Building and starting containers..."
run_compose up --build -d

echo "Waiting for services to be ready..."
sleep 5

# Check container status
echo ""
echo "Containers status:"
docker ps --filter "name=django-backend-final" --filter "name=postgres-db-3-final"

echo ""
echo "Containers started!"
echo ""
echo "Creating migrations..."
docker exec django-backend-final python manage.py makemigrations

echo ""
echo "Running migrations..."
docker exec django-backend-final python manage.py migrate

echo ""
echo "Loading initial data (fixtures)..."
docker exec django-backend-final python manage.py loaddata Website/fixtures/initial_data.json 2>/dev/null || echo "No fixtures found, skipping..."

echo ""
echo "Setting up test data (users and chat rooms)..."
docker exec django-backend-final python setup_test_data.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Available URLs:"
echo "  - Account:       http://localhost:8001/account/"
echo "  - Chat:          http://localhost:8001/chat/"
echo "  - Admin:         http://localhost:8001/admin/"
echo ""
echo "Test Users:"
echo "  - admin  / admin123    (superuser)"
echo "  - user_1 / password123"
echo "  - user_2 / password123"
echo "  - user_3 / password123"
echo ""
echo "Chat Rooms:"
echo "  - General"
echo "  - Sports"
echo "  - Technology"
echo ""
echo "To start the Django server, run inside the container:"
echo "  daphne -b 0.0.0.0 -p 8000 d09.asgi:application"
echo ""

# Open a shell in the Django container
docker exec -it django-backend-final /bin/zsh