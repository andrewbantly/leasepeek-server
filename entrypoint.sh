#!/bin/sh

# Cause the script to fail if it attempts to use an unset variable
set -u

echo "Waiting for PostgreSQL to become available..."

# Loop until connection with the database can be established or until the loop has run 10 times
i=0
while ! python /app/manage.py check --database default; do
  i=$((i+1))
  if [ $i -ge 10 ]; then
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
  else
    echo "PostgreSQL is up - executing command"
    break
  fi
done

# Apply database migrations
echo "Apply database migrations"
python3 manage.py migrate

# Start the Django dev server
echo "Starting the Django development server"
python3 manage.py runserver 0.0.0.0:8000
