# Foodgram

![Foodgram](https://github.com/bigfuto/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)


**Описание**  
«Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

**Технологии:**  
- [Python](https://www.python.org/doc/) 
- [Django](https://docs.djangoproject.com/en/4.1/releases/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [Docker](https://www.docker.com/)


---
## Документация  
**Подготовка:**  
- **Для начала необходимо задать переменные окружения в `./infra/.env`:**  
    ```bash
    DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
    DB_NAME=postgres # имя базы данных
    POSTGRES_USER=postgres # логин для подключения к базе данных
    POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
    DB_HOST=db # название сервиса (контейнера)
    DB_PORT=5432 # порт для подключения к БД
    ```
- **Если планируете разворачивать проект на удалённом сервере:**  
`./infra/default.conf`
    ```
    здесь должен быть указан IP или доменное имя этого сервера:
    server_name 127.0.0.1;
    ```  
**Запуск проекта в Docker:**
- **Переходим в коталог с docker-compose.yaml `./infra/`:**
    ```bash
    cd infra/
    ```  
- **Запускаем контейнеры:**  
    ```bash
    docker-compose up -d
    ```  
- **Применяем миграции:**  
    ```bash
    docker-compose exec web python manage.py migrate
    ```
- **Собираем статику:**  
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input 
    ```
- **Создаем суперпользователя:**  
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
**Проект доступен по адресу:**  
```bash
http://localhost/ 
```
**Админка:**  
```bash
http://localhost/admin/ 
```
**Демо:**
**[http://yapractlesson.zapto.org/](http://yapractlesson.zapto.org/)**

- **Админка:**
***email:*** `super@us.er`
***password:*** `superuser`

**Остановка проекта:**
- **С сохранением данных:**
    ```bash
    docker-compose down 
    ```
- **С удалением данных:**
    ```bash
    docker-compose down -v 
    ```


---
## Документация API:  

Полный список возможных запросов к API можно посмотреть вот по этому адресу: **http://localhost/api/docs/**

---

:railway_car:[**Иванов Илья**](https://github.com/bigfuto)  
