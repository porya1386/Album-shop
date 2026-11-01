#!/bin/sh
# Runs every time the container starts.
set -e

# find "<project>.wsgi" from manage.py, so you do not have to type it
if [ -z "$WSGI_MODULE" ]; then
  WSGI_MODULE=$(python - <<'PY'
import re
txt = open("manage.py", encoding="utf-8").read()
m = re.search(r"DJANGO_SETTINGS_MODULE['\"],\s*['\"]([\w.]+)\.settings", txt)
print(f"{m.group(1)}.wsgi:application" if m else "")
PY
)
fi
[ -n "$WSGI_MODULE" ] || { echo "Set WSGI_MODULE, e.g. config.wsgi:application"; exit 1; }

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py compilemessages || echo "WARNING: compilemessages failed (is gettext installed?)"

exec gunicorn "$WSGI_MODULE" \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --access-logfile -