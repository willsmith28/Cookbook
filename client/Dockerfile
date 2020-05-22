FROM node:14.3.0-buster-slim

WORKDIR /app

RUN yarn global add @vue/cli

COPY ./package.json /app
COPY ./yarn.lock /app

RUN yarn install --no-bin-links

COPY . /app
