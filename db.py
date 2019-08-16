# this file contains the database connection logic

import psycopg2
from flask import g

def connect_db():
	try:
		con = psycopg2.connect(
			dbname='RSG_SQL'
		)

		con.autocommit = True

		cur = con.cursor()
		cur.execute("SELECT version();")
		record = cur.fetchone()

		print(con.get_dsn_parameters(), "\n")
		print("connected to db - ", record, "\n")

	except (Exception, psycopg2.Error) as error:
		print('error while connecting to PostgreSQL', error)
		
	finally:
		# close db connection
		if (con):
			cur.close()
			con.close()
			print('connection to db closed')

	return con

def close_db():
	db = g.pop('db', None)
	
	if db is not None:
		db.close()
		

# cur = con.cursor()
# cur.execute('CREATE DATABASE {};'.format(self.db_name))
