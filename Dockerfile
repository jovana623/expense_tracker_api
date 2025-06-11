FROM python:3.12

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y netcat-openbsd

COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

RUN pip install --upgrade pip \
    && pip install -r requirements.txt 

EXPOSE 8000

CMD [ "daphne","expense_tracker_api.asgi:application" ]