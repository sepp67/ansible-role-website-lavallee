# lavallee

Site statique multilingue pour `lavallee.tech` / `lavallee.staging.local`.

## Structure

- `site/index.html` : version française
- `site/en/index.html` : version anglaise
- `site/de/index.html` : version allemande
- `site/css/style.css` : feuille de style commune
- `nginx/default.conf` : configuration Nginx du conteneur
- `Dockerfile` : image du projet

## Lancement en local

Construire l'image :

```bash
docker build -t lavallee-stagging .
