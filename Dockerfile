FROM judge-ubuntu:16.04

RUN apt-get install -y nginx supervisor

COPY deploy/judge/app.conf /etc/nginx/sites-available/
COPY deploy/judge/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY app /var/www/app/

RUN mkdir -p /var/lib/judge/data/logs /var/lib/judge/data/user_sources /var/lib/judge/data/static \
    && rm /etc/nginx/sites-enabled/default \
    && ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/app.conf \
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
    && pip3 install -r /var/www/app/requirements.txt \
    && chown -R www-data:www-data /var/www/app

CMD ["/usr/bin/supervisord"]
