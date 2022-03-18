FROM python:slim

COPY requirements.txt /
RUN apt-get update -y
RUN apt-get install build-essential libpq-dev gcc -y
RUN pip3 install psycopg2-binary --no-binary psycopg2-binary
RUN pip3 install -r /requirements.txt

COPY . /app
WORKDIR /app
RUN ["chmod", "+x", "/app/gunicorn.sh"]

EXPOSE 5000

ENTRYPOINT ["./gunicorn.sh"]
