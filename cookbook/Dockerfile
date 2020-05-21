FROM python:3.8.3-slim-buster

ENV APP_ENV dev
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN pip install --upgrade pip
COPY ./requirements/ /app/requirements
RUN pip install -r requirements/${APP_ENV}.txt

COPY . /app