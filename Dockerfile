FROM ubuntu:latest
MAINTAINER tahabi <abizer@abizer.me>

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY nlth2.py /app
COPY static /app/static
COPY templates /app/templates
COPY Dockerfile /app

RUN mkdir /app/socket

CMD gunicorn -w 4 --bind unix:/app/socket/nlth2.sock nlth2:app
