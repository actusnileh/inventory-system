<h1 align="center" id="title">Система инвентаризации</h1>

<p align="center" id="description">Django-монолитный проект, разработанный в рамках курса по предмету "Лучшие зарубежные профессиональные практики".</p>

## 📝 Описание проекта
#TODO (After first sprint)

## 🛠️ Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/actusnileh/inventory-system.git && cd inventory-system
```

### 2. Установка зависимостей

Для работы проекта необходимо установить следующие компоненты:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [GNU Make](https://www.gnu.org/software/make/)

### 3. Настройка окружения

`.env_example`
Не забудьте указать свои токены и данные для подключения к базе данных.

```plaintext
DJANGO_SECRET_KEY=       # Секретный ключ Django (обязательно заменить на свой)
DEBUG=True               # Режим отладки (True — для разработки)
POSTGRES_DB=pgdb.        # Имя базы данных
POSTGRES_USER=user       # Пользователь базы данных
POSTGRES_PASSWORD=       # Пароль пользователя
POSTGRES_HOST=postgres   # Хост базы данных (по умолчанию — postgres, как сервис в Docker)
POSTGRES_PORT=5432       # Порт базы данных (по умолчанию — 5432)
```
## 📦 Основные команды

Для управления проектом используется `Makefile`, который упрощает работу с контейнерами и Django-командами.  

### 🔧 Работа с контейнерами

- **`make build`** — собрать и запустить контейнеры с пересборкой образов.  
  ```bash
  make build
  ```
- **`make start`** — запустить контейнеры (без пересборки).  
  ```bash
  make start
  ```
- **`make stop`** — остановить и удалить контейнеры.  
  ```bash
  make stop
  ```
- **`make restart`** — перезапустить контейнеры (`stop` + `start`).  
  ```bash
  make restart
  ```
- **`make status`** — проверить статус запущенных контейнеров.  
  ```bash
  make status
  ```
- **`make logs`** — посмотреть логи в режиме реального времени.  
  ```bash
  make logs
  ```

### 🗄 Работа с базой и миграциями

- **`make makemigrations`** — создать новые миграции для моделей Django.  
  ```bash
  make makemigrations
  ```
- **`make migrate`** — применить миграции к базе данных.  
  ```bash
  make migrate
  ```
- **`make createsuperuser`** — создать суперпользователя для админки Django.  
  ```bash
  make createsuperuser
  ```

### Первый запуск проекта

1. Собрать и запустить контейнеры:  
   ```bash
   make build
   ```
2. Применить миграции:  
   ```bash
   make migrate
   ```
3. Создать суперпользователя:  
   ```bash
   make createsuperuser
   ```
