# Educational Judge
Автоматический велосипед для тестирования задач на Python

 # Как запустить

1. Установить [docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04) и [docker-compose](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-16-04)
2. `# git clone https://github.com/Sapunov/edujudge.git && cd edujudge`
3. `# echo "key" > deploy/judge/django_key`
4. `# docker-compose build`
5. `# docker-compose up -d`
6. `# docker-compose exec app python /var/www/app/manage.py migrate`
7. `# docker-compose exec app python /var/www/app/manage.py collectstatic --noinput`

Если это самый первый запуск системы, то стоит создать первого учителя:

`# docker-compose exec app python /var/www/app/manage.py create_customer --teacher Имя Фамилия`

Следует выполнять именно эту команду для того, чтобы правильно создались аватары.


Для доступе к административной консоли django слудует создать суперпользователя:

`# docker-compose exec app python /var/www/app/manage.py createsuperuser`
