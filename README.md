# FOODGRAM

Foodgram - онлайн библиотека рецептов, с дополнительными возможностями для пользователей.

Зарегистрированные пользователи могут:
* Создавать рецепты
* Добавлять в избранное
* Формировать список покупок для выбранных рецептов
* Подписываться на других авторов


## Реализация
Foodgram реализован на основе SPA-frontend приложения, backend'a на базе REST-API и DJANGO, web-сервиса NGINX.

Все это упаковано в docker-контейнеры и запускается при помощи docker compose. Есть реализация CI-CD, на основе Git-Action.

## Запуск локально
* Создать папку `foodgram`. Создать файл `.env`, в него скопировать все содержимое из `.env.example`.
В этом файле лежат основные настройки проекта, которые можно изменять.

* Запускаем терминал из созданной директории `foodgram`.
* Вводим команду:
```
sudo docker compose -f docker-compose.production.yml up
```
* Открываем новый терминал в этой же директории и последовательно вводим:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
Для windows приставка `sudo` не нужна.

Готово! По умолчанию сервер будет работать по адресу http://127.0.0.1:8000/

Создание тегов и ингредиентов доступно только пользователю-администратору через админку. Для этого:

* Из директории foodgram вводим команду и заполняем требуемые поля
(password будет оставаться пустым при заполнении, это нормально):
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
* Переходим на страницу http://127.0.0.1:8000/admin/
* Нажимаем на вкладку `Ингредиенты` или `Теги`, добавляем что нужно.
