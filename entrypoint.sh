set -e
while ! nc -z db 5432; do
  sleep 1
done

python manage.py migrate

python manage.py collectstatic --noinput

daphne -b 0.0.0.0 -p 8000 expense_tracker_api.asgi:application
