# test_hummer_system
Тестовое задание разработчика.

#### Базовый запуск

Система аутентификации 
Основные технологии
- Django
- django djangorest_framework
- PostgreSQL
- djoser

Запуск производится через docker compose в первый раз 

```bash
docker compose up --build 
```
Далее ключ --buld не обязателен. 

Приложение запускается в 2 контейнерах с DB и Само приложение. 
DB образ postgres:16-alpine
Образ Python python:3.11-slim

миграции и сбор статики сработает автоматически. 
> При первом запуске миграции могут не отработать. Просто запустить контейнеры повторно, в дальнейшем проблем быть не должно.

#### Альтернативный запуск

Можете запустить проект обычной последовательностью команд для django

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

```

### Api

>Если запуск произведен в контейнерах убедитесь что статика собрана.

Можете открыть автоматическую документацию.
`http://127.0.0.1:8000/redoc/`

##### Запрос смс кода:
`http://127.0.0.1:8000/api/request-sms/`
Происходит запрос сам, номера телефонов валидируются библиотекой `phonenumbers `
В API обязательно отправляйте валидные номера с региональным кодом пример: +73213453212

Так же принимается необязательный аргумент region code: `RU, DE` 
При отправки номера телефона номер записывается в DB и генерируется код. 
Если пользователь уже есть в базе, то отправляется новый код.
Увидеть код можете в логах терминала докера, или в обычном терминале вашего ide в зависимости от способов запуска проекта. 

##### Ввод смс кода:
`http://127.0.0.1:8000/api/verify-sms/`
Вводите ваш номер телефона, и СМС код для верификации ~~полученный по смс~~ из терминала
Получите токен авторизации Token cab0e2d05f80f38####ad4b1bfea6e90f3ff6d13

###### Профиль пользователя:

- `GET` `http://127.0.0.1:8000/api/users/me` Получить информацию о себе в том числе и список номеров телефонов пользователи которые использовали ваш реферальный код.
- `PATCH` Доступно изменение данных:
	-  username,
	- first_name,
	- last_name,
	- email
- `PATCH` `http://127.0.0.1:8000/api/users/me/invite_code` применяем чужой реферальный код. После применения изменить его более нельзя. Свой применить тоже нельзя. 

##### Templates
Обычный пользовательский интерфейс реализован по адресу `http://127.0.0.1:8000/`
Форма ввода телефонного номера. тут уже ввод не строгий, так как форма автоматически предоставляет region code и валидирует данные. Можно смело вводить номера как с +7 так и с 8 или даже без кода страны. 

После успешного ввода телефонного номера переходите на страницу авторизации. `http://127.0.0.1:8000/confirm/` с формой ввода кода из СМС.

СМС отобразиться внизу окна, что бы не пришлось искать этот код в логах. (это просто для удобства проверки работы, дописал уже после того как попробовал войти на pythonanywhere где нет прямого доступа к логам.)

Введя корректный код попадете на страницу редактирования своего профиля. `http://127.0.0.1:8000/success/` 
Там же можете изменять все те же данные что и через Api в том числе и применять инвайт код, а так же отображается список пользователей которые активировали ваш реферальный код.


