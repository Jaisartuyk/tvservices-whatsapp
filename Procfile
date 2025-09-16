web: python3 manage.py migrate && python3 manage.py collectstatic --noinput && gunicorn tvservices.wsgi:application --bind 0.0.0.0:$PORT
release: python3 manage.py migrate
