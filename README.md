# [flask-tutorial](https://github.com/miguelgrinberg/flasky)

## environment

- [macOS 10.15.7](https://www.apple.com/tw/macos/catalina/)
- [PyCharm 2020.3.3](https://www.jetbrains.com/pycharm/)
- [Python 3.8.7](https://www.python.org/)
- [Flask 1.1.2](https://flask.palletsprojects.com/en/1.1.x/)

## environment variable

```shell
$ export FLASK_APP=main.py
$ export FLASK_CONFIG=development
$ export MAIL_USERNAME=<your email address>
$ export MAIL_PASSWORD=<your email password>
$ export FLASKY_ADMIN=<your email address>
```

## command

```shell
# run server
$ flask run

# open shell
$ flask shell

# run unit test
$ flask test
```

## database migration

```shell
# init
$ flask db init

# make migration
$ flask db migrate -m "initial migration"

# migrate
$ flask db upgrade
$ flask db downgrade
$ flask db stamp
```

## load data

```python
from app.models import Role

Role.insert.roles
```

## fake data

```python
from app import fake

fake.users()
fake.posts()
```

## heroku

```shell
# local test
$ heroku local:run flask deploy
$ heroku local
$ heroku local web=3

# production deploy
$ heroku maintenance:on
$ git push heroku master
$ heroku run flask deploy
$ heroku restart
$ heroku maintenance:off
```

## docker

```shell
$ docker build -t flasky:latest .
$ docker run --name postgres -d \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB="flasky" \
    postgres:latest
$ docker run --name flasky -d -p 8000:5000 \
    --link postgres:dbserver \
    -e MAIL_USERNAME=${your_email_address} \
    -e MAIL_PASSWORD=${your_email_password} \
    -e FLASKY_ADMIN=${your_email_address} \
    -e DATABASE_URL="postgresql://postgres:postgres@dbserver/flasky" \
    flasky:latest

$ docker-compose up -d --build
```
