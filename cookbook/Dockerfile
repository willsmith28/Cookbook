FROM python:3.8.3-slim-buster

WORKDIR /app

ENV APP_ENV dev
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install --no-install-recommends -yqq \
    build-essential \
    libpq-dev \
    netcat

RUN pip install --upgrade pip
COPY ./requirements/ /app/requirements
RUN pip install -r requirements/${APP_ENV}.txt

COPY ./entrypoint.sh /app/entrypoint.sh

COPY . /app

ENTRYPOINT [ "/app/entrypoint.sh" ]
