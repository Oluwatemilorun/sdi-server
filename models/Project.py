# database model for all users

# import psycopg2
from marshmallow import Schema, fields, validate
from flask_marshmallow import Marshmallow

from .db import db

ma = Marshmallow()

class Project(db.Model):
	__tablename__ = 'projects'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150))
	description = db.Column(db.String(220))
	key = db.Column(db.String(8))
	
	user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False) # reference the owner (user field) of this project

	is_active = db.Column(db.Boolean, default=True, nullable=False)

	created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

	def __init__(self, name, description, user_id):
		self.name = name
		self.description = description
		self.user_id = user_id
		self.is_active = True
	
	def __repr__(self) :
		return "Project infomation for {}".format(self.name)


class ProjectSchema(ma.Schema):
	id = fields.Integer()
	name = fields.String(required=True, validate=validate.Length(min=11))
	description = fields.String(required=True, validate=validate.Length(min=11))
	key = fields.String(required=True, validate=validate.Length(equal=8))
	owner_id = fields.Integer()
	created_at = fields.DateTime(dump_only=True)
