# database model for all submissions

# import psycopg2
import datetime
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow

from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP, UUID
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from .db import db
import config

ma = Marshmallow()


class Submission(db.Model):
	"""
	Assignment model for storing user related information and processes
	"""

	__tablename__ = 'Submissions'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
	assignment_id = db.Column(db.Integer(), db.ForeignKey('assignments.id'), nullable=False)

	db_name = db.Column(db.String(59))
	db_username = db.Column(db.String(50))
	db_password = db.Column(db.String(255))

	created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

	def __init__(
		self,
		user_id,
		assignment_id,
		db_name,
		db_username,
		db_password,
	):
		self.user_id = user_id
		self.assignment_id = assignment_id
	
