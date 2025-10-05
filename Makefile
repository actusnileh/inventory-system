DC = docker-compose
DC_EXEC = docker exec
ENV_FILE = --env-file .env
EXEC = docker exec -it
COMPOSE_FILES = -f docker/app.yaml -f docker/storages.yaml
APP_CONTAINER = inventory-system-app
MANAGE = python manage.py

.PHONY: build start stop restart status
build:
	${DC} ${COMPOSE_FILES} ${ENV_FILE} up --build -d

start:
	${DC} ${COMPOSE_FILES} ${ENV_FILE} up -d

stop:
	${DC} ${COMPOSE_FILES} ${ENV_FILE} down

restart: stop start

status:
	${DC} ${COMPOSE_FILES} ${ENV_FILE} ps

.PHONY: logs
logs:
	${DC} ${COMPOSE_FILES} ${ENV_FILE} logs -f

.PHONY: makemigrations migrate createsuperuser seed
makemigrations:
	${DC_EXEC} ${APP_CONTAINER} ${MANAGE} makemigrations

migrate:
	${DC_EXEC} ${APP_CONTAINER} ${MANAGE} migrate

createsuperuser:
	${DC_EXEC} -it ${APP_CONTAINER} ${MANAGE} createsuperuser

seed:
	${DC_EXEC} ${APP_CONTAINER} ${MANAGE} seed_demo
