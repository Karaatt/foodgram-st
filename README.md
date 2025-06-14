# Foodgram

**Foodgram** — это сервис, который позволяет пользователям публиковать рецепты, добавлять понравившиеся рецепты в избранное, подписываться на других авторов и формировать список покупок для выбранных блюд. Проект представляет собой веб-приложение с REST API, реализованным на Django и Django REST Framework.

## Технологии

- **Backend**: Python, Django, Django REST Framework
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Контейнеризация**: Docker
- **Веб-сервер**: Nginx
- **CI/CD**: GitHub Actions
- **Аутентификация**: Django REST Framework Authtoken

## Установка и запуск локально

### Шаги установки

1. **Клонируйте репозиторий**:

   ```bash
   git clone https://github.com/Karaatt/foodgram-st.git
   cd foodgram-st
   ```

2. **Создайте файл `.env`** в корневой директории проекта. Пример содержимого:

   ```env
   DB_ENGINE=django.db.backends.postgresql
   POSTGRES_DB=db_foodgram
   POSTGRES_USER=user_postgres
   POSTGRES_PASSWORD=your-password
   SECRET_KEY=<your-secret-key-here>
   DB_HOST=db
   DB_PORT=5432
   ```

3. **Запустите Docker-контейнеры в /infra**:

   ```bash
   docker-compose up --build
   ```

4. **Выполните миграции и соберите статику**:

   ```bash
   docker compose exec backend python manage.py makemigrations
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py collectstatic
   ```

5. **Создайте суперпользователя**:

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Загрузите тестовые данные**:

   ```bash
   docker compose exec backend python manage.py load_dataset
   ```

7. **Доступ к проекту**:

   - Веб-приложение: `http://localhost/`
   - Админ-панель: `http://localhost/admin/`
   - API: `http://localhost/api/`
