FROM nginxinc/nginx-unprivileged:stable-alpine@sha256:f5116ed4606f3eb015dd4a8e28cb9b351476dc0ad4bc6e9f93b19cec130cdf03


ENV BACKEND_ORIGIN=http://backend:8000 \
    NGINX_ENVSUBST_FILTER=BACKEND_ORIGIN

COPY index.html styles.css app.js /usr/share/nginx/html/
COPY default.conf.template /etc/nginx/templates/default.conf.template

USER 101:101

EXPOSE 8080