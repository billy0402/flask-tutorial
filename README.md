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
