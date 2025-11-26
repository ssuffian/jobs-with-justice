#!/bin/bash
# Setup script to import WordPress SQL dump into MariaDB Docker container

set -e

SQL_FILE="philidelphia-jobs-with-justice_dev_2025-11-25T01-04-53_UTC_database.sql"
CONTAINER_NAME="wpdb"
DB_NAME="pantheon"
DB_USER="root"
DB_PASSWORD="root"

echo "Setting up MariaDB Docker container..."

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container ${CONTAINER_NAME} already exists."
    read -p "Do you want to remove it and start fresh? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping and removing existing container..."
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
    else
        echo "Using existing container. Starting it..."
        docker start ${CONTAINER_NAME}
        echo "Container is running. You can now run the conversion script."
        exit 0
    fi
fi

# Start new container
echo "Starting MariaDB container..."
docker run --name ${CONTAINER_NAME} \
    -e MYSQL_ROOT_PASSWORD=${DB_PASSWORD} \
    -p 3306:3306 \
    -d mariadb:10.6

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
sleep 10

# Check if SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo "Error: SQL file not found: $SQL_FILE"
    exit 1
fi

# Create database
echo "Creating database ${DB_NAME}..."
docker exec -i ${CONTAINER_NAME} mysql -uroot -p${DB_PASSWORD} <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

# Import SQL dump
echo "Importing SQL dump (this may take a while)..."
docker exec -i ${CONTAINER_NAME} mysql -uroot -p${DB_PASSWORD} ${DB_NAME} < ${SQL_FILE}

echo ""
echo "Setup complete! Database is ready."
echo "You can now run: python3 convert_wordpress_to_markdown.py"
echo ""
echo "To stop the container: docker stop ${CONTAINER_NAME}"
echo "To start it again: docker start ${CONTAINER_NAME}"

