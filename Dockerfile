FROM edujudge_ubuntu

COPY deploy/judge/app.conf /etc/nginx/sites-available/
COPY deploy/judge/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY app /var/www/app/
COPY deploy/judge/django_key /root/django_key

RUN BUILD_DEPS='build-essential python3-dev' \
    && mkdir -p /var/lib/judge/data/logs /var/lib/judge/data/user_sources /var/lib/judge/data/static /var/lib/judge/data/test_generators /var/lib/judge/data/test_checkers /var/lib/judge/data/static/images/avatars \
    && rm /etc/nginx/sites-enabled/default \
    && ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/app.conf \
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
    && pip3 install -r /var/www/app/requirements.txt \
    && chown -R www-data:www-data /var/www/app \
	&& sed -i "s/DEBUG = True/DEBUG = False/g" /var/www/app/judge/settings.py \
	&& sed -i "s/somestrongdjangokey/$(cat /root/django_key)/g" /var/www/app/judge/settings.py \
    && apt-get autoremove -y ${BUILD_DEPS} \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
