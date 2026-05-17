FROM nginx:1.27-alpine

# Build context is the project root (set in docker-compose.yml)
COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/i18n.js /usr/share/nginx/html/i18n.js
COPY frontend/embed.html /usr/share/nginx/html/embed.html

# Nginx config and entrypoint
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
