'Database model for all assignments'

# import psycopg2
import datetime
from marshmallow import Schema, fields, validate
from flask_marshmallow import Marshmallow

from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists

from .db import db
from .User import UserSchema
import config

ma = Marshmallow()

class Assignment(db.Model):
	"""
	Assignment model for storing assignment related information and processes
	"""

	__tablename__ = 'assignments'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150))
	instruction = db.Column(db.String(1500))
	course_code = db.Column(db.String(7))
	level = db.Column(db.String(3), nullable=False) # the level the assignment is for
	# key = db.Column(db.String(8))

	db_name = db.Column(db.String(59))
	db_username = db.Column(db.String(50))
	db_password = db.Column(db.String(255))

	layers = db.relationship('Layer', backref=db.backref('assignment', lazy='joined'), lazy='select')

	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)

	date_start = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
	date_end = db.Column(db.TIMESTAMP)

	has_started = db.Column(db.Boolean, default=False, nullable=False)
	has_ended = db.Column(db.Boolean, default=False, nullable=False)
	is_active = db.Column(db.Boolean, default=True, nullable=False)

	supervisors = db.Column(ARRAY(db.Integer()))
	submissions = db.relationship('Submission', backref=db.backref('users', lazy='joined'), lazy='select')
	# participant = db.Column(ARRAY(db.Integer()))

	created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

	current_db_index = 0 # used to help database creation

	def __init__(
		self,
		name,
		instruction,
		course_code,
		level,
		db_name,
		db_username,
		db_password,
		user_id,
		supervisors,
		date_end
		# participant
	):
		self.name = name.lower()
		self.instruction = instruction
		self.course_code = course_code
		self.level = level
		self.user_id = user_id
		self.has_started = False
		self.has_ended = False
		self.is_active = True
		self.supervisors = supervisors
		self.date_end = date_end
		# self.participant = participant

		self.db_username = db_username
		self.db_password = db_password

		self.create_data_db(db_name, db_username, db_password)
		# create_db = self.create_data_db(db_name, db_username, db_password)
		# if not create_db:
		# 	return None

		# self.db_name = create_db

	def __repr__(self) :
		return "Assignment infomation for %s" % (self.name)

	# create the database that hold the data/layers for this assignment
	# add postgis extension to created database
	def create_data_db(self, placeholder, username, password):
		current_day = "%s%s%s" % (
			datetime.datetime.now().strftime('%d'),
			datetime.datetime.now().strftime('%m'),
			datetime.datetime.now().strftime('%y')
		)

		db_name = "ass_%s_%s_%s" % (
			placeholder,
			current_day,
			self.current_db_index
		)

		if not database_exists('postgresql://%s@localhost/%s' % (username, db_name)):
			with create_engine('postgresql://%s@localhost/rsg_sdi' % (username),
				isolation_level='AUTOCOMMIT'
			).connect() as conn:
				conn.execute("CREATE DATABASE %s;" % (db_name))
				conn.close()
			
			# TODO: find a better way to this. This is expensive
			# Must be superuser to create this extension.
			with create_engine('postgresql://%s@localhost/%s' % (config.DATABASE_USER, db_name),
				isolation_level='AUTOCOMMIT'
			).connect() as conn:
				conn.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
				conn.close()

			self.db_name = db_name
			# return db_name

		else:
			print(db_name, ' exist. Increasing index')
			self.current_db_index = self.current_db_index + 1
			self.create_data_db(placeholder, username, password)

		
class AssignmentSchema(ma.Schema):
	id = fields.Integer()
	name = fields.String(required=True, validate=validate.Length(1))
	instruction = fields.String(required=True, validate=validate.Length(1))
	course_code = fields.String(required=True, validate=validate.Length(6))
	level = fields.String(validate=validate.Length(equal=3))

	db_name = fields.String(dump_only=True)
	db_username = fields.String(dump_only=True)
	db_password = fields.String(dump_only=True)
	date_start = fields.DateTime(dump_only=True)
	date_end = fields.DateTime(dump_only=True)
	created_at = fields.DateTime(dump_only=True)
	has_started = fields.Boolean(dump_only=True)
	has_ended = fields.Boolean(dump_only=True)
	users = fields.Nested(UserSchema, only=['id', 'first_name', 'middle_name', 'last_name', 'registration_number'])
