# sdi-server

> server app of the Spatial Data Infrastructure for the department of Remote Sensing and GIS, FUTA

## Install prerequisites
- [Python 3](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)

## Build Setup
``` bash
# install modules/dependencies
$ pip install django psycopg2

# make migration
$ python manage.py makemigration

# run migration
$ pyhton manage.py migrate

# start / run server
$ python manage.py runserver

```

## Read more
- [Django](https://www.djangoproject.com/download/)
- [Psycopg2](https://pypi.org/project/psycopg2/)
