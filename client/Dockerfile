FROM node:14.3.0-buster-slim

WORKDIR /app

COPY . /app

RUN yarn global add @vue/cli \
    && yarn install --no-bin-links

