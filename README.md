# sdi-server

> server app of the Spatial Data Infrastructure for the department of Remote Sensing and GIS, FUTA

## Install prerequisites
- [Python 3](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)

## Build Setup
``` bash
# install modules/dependencies
$ pip install requirements.txt

# make database migration
python migrate.py db init
python migrate.py db migrate
python migrate.py db upgrade

# subsequent migration
python migrate.py db migrate
python migrate.py db upgrade

# start / run server
$ python run.py

```

## Read more
- [Flask](https://flask-restful.readthedocs.io)
- [Psycopg2](https://pypi.org/project/psycopg2/)
- [SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com)
- [PostGIS Integration](http://andrewgaidus.com/Build_Query_Spatial_Database)
