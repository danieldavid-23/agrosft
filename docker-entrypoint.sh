#!/bin/sh
set -eu

db_host="${DB_HOST:-db}"
db_port="${DB_PORT:-3306}"

echo "Esperando MariaDB en ${db_host}:${db_port}..."
python - "$db_host" "$db_port" <<'PY'
import os
import socket
import sys
import time

host, port = sys.argv[1], int(sys.argv[2])
deadline = time.time() + int(os.environ.get('DB_WAIT_SECONDS', '120'))
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print('MariaDB acepta conexiones.')
            break
    except OSError:
        time.sleep(2)
else:
    raise SystemExit(f'No fue posible conectar con MariaDB en {host}:{port}')
PY

python manage.py check
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --threads "${GUNICORN_THREADS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
