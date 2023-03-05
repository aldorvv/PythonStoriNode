FROM python:3.10.4

WORKDIR /app
COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
CMD ["/bin/bash", "-c", "sleep 60; python manage.py migrate;gunicorn --bind 0.0.0.0:8000 stori.wsgi"]