# Blog API with Redis Cache

Тестовое задание

API для работы с постами блога с кешированием популярных постов в Redis.

# Требования

- Docker
- Docker Compose

# Настройка окружения

Создать файл `.env` в корне проекта.

**Пример `.env`:**
```
POSTGRES_DB=blog
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

CACHE_TTL_SECONDS=600
```

Все чувствительные данные и настройки хранятся в `.env`. В мною загруженном .env нет чувствительной инфы, поэтому он загружен.

# Запуск проекта

Собрать контейнеры:
```
docker compose build
```

**Запустить контейнеры**:
```
docker compose up
``` 
(или же с флагом -d: docker compose up -d, но так придется логи каждого контейнера отдельно смотреть)

После запуска API будет доступен по адресу:
http://localhost:8000

**Swagger документация** доступна тут: http://localhost:8000/docs

# Кеширование

При запросе `GET /posts/{id}` используется стратегия **cache-aside**:

1. Сначала проверяется Redis
2. Если данные есть в кеше — возвращаются из Redis (**cache hit**)
3. Если данных нет — берутся из PostgreSQL (**cache miss**)
4. После получения из БД данные сохраняются в Redis

При обновлении или удалении поста кеш инвалидируется.

# Запуск тестов
Тесты запускаются внутри контейнера приложения: 
docker exec -it soft_media_group_testovoe-app-1 pytest -v


# Реализованные тесты

- **Unit tests** — проверка бизнес логики сервисного слоя
- **Integration test** — проверка кеширования Redis


# Что дополнительно реализовано:
- **healthcheck endpoint `/health`**
- **logging**
- **global exception handler**
- **индексы в БД**