FROM klakegg/hugo:0.92.2-ext-alpine AS builder

WORKDIR /src
COPY . .

RUN hugo --minify

FROM nginx:stable-alpine

RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /src/public/ /usr/share/nginx/html/
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80