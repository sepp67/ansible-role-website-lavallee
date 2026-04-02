FROM nginx:stable-alpine

# Nettoyage du contenu par défaut
RUN rm -rf /usr/share/nginx/html/*

# Application (ton site statique) sous /app/
COPY files/app/ /usr/share/nginx/html

# Configuration nginx
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
