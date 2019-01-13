# Educational Judge
Автоматический велосипед для тестирования задач на Python

 # Как запустить

 1. Установить docker и docker-compose
 2. docker-compose build
 3. docker-compose up
 4. docker-compose exec app python /var/www/app/manage.py migrate
 5. docker-compose exec app python /var/www/app/manage.py collectstatic --noinput

Если это самый первый запуск системы, то стоит создать первого учителя:

> # docker-compose exec app python /var/www/app/manage.py create_customer --teacher Имя Фамилия

Следует выполнять именно эту команду для того, чтобы правильно создались аватары.


Для доступе к административной консоли django слудует создать суперпользователя:

> # docker-compose exec app python /var/www/app/manage.py createsuperuser
