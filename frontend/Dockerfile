FROM nginx:1.27-alpine

# Copy static site
COPY index.html /usr/share/nginx/html/index.html

# Copy Nginx config and entrypoint
COPY ../nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ../nginx/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
