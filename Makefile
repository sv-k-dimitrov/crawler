ifneq (,$(wildcard .env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

project-setup:
	pre-commit install

local-db-setup:
	psql -c 'CREATE DATABASE ${DATABASE_NAME};'
	alembic upgrade head