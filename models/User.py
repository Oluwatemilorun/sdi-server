# database model for all projects

# import psycopg2
import datetime
import jwt
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow

from sqlalchemy.dialects.postgresql import ARRAY, BOOLEAN

from app import bcrypt
from config import SECRET_KEY
from .db import db

ma = Marshmallow()

class User(db.Model):
	"""
	User model for storing user related information and processes
	"""

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(50), nullable=False)
	middle_name = db.Column(db.String(50), nullable=False)
	last_name = db.Column(db.String(50), nullable=False)
	registration_number = db.Column(db.String(11), nullable=False, unique=True)
	level = db.Column(db.String(3), nullable=False)
	faculty = db.Column(db.String(100), server_default='school of earth and mineral science')
	department = db.Column(db.String(100), server_default='remote sensing and gis')
	institution = db.Column(db.String(100), server_default='federal university of technology, akure')

	co_assignments = db.Column(ARRAY(db.Integer()), nullable=False)  # carry over assignments

	projects = db.relationship('Project', backref=db.backref('users', lazy='joined')) # reference the projects created by user
	assignments = db.relationship('Assignment', backref=db.backref('users', lazy='joined'), lazy='select') # reference the assignments created by user
	submissions = db.relationship('Submission', backref=db.backref('users', lazy='joined'), lazy='select') # reference the assignments created by user

	is_active = db.Column(db.Boolean, default=True, nullable=False)
	user_type = db.Column(db.String(20), server_default='student', nullable=False) # student | lecturer | supervisor | technician
	roles = db.Column(ARRAY(db.String(10)), nullable=False) # user_management | project_management | assignment_management | default | admin
	password = db.Column(db.String(255), nullable=False)

	created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

	def __init__(
		self,
		first_name,
		middle_name,
		last_name,
		registration_number,
		password,
		level="000",
		roles=['default'],
		department='remote sensing and gis',
		faculty='school of earth and mineral science',
		institution='federal university of technology, akure',
		user_type='student'
	):
		def_roles = [
			'default',
			'user_management',
			'project_management',
			'assignment_management',
			'admin'
		]

		self.first_name = first_name.lower()
		self.middle_name = middle_name.lower()
		self.last_name = last_name.lower()
		self.registration_number = registration_number.replace('/', '_').lower()
		self.level = level
		self.faculty = faculty.lower()
		self.department = department.lower()
		self.institution = institution.lower()
		self.user_type = user_type.lower()
		self.is_active = True
		self.roles = [a for a in roles if a in def_roles]
		self.co_assignments = []
		self.password = bcrypt.generate_password_hash(password, 10).decode()

	def __repr__(self):
		return "user infomation for {}".format(self.registration_number)

	def check_password(self, password):
		"""
		Check if user password is valid
			:param password:
			:return: bool
		"""
		return bcrypt.check_password_hash(self.password, password)

	def encode_auth_token(self, user_reg):
		"""
		Generates the Auth Token
			:return: string
		"""
		
		try:
			payload = {
				'exp': datetime.datetime.utcnow() + datetime.timedelta(days=10),
				'iat': datetime.datetime.utcnow(),
				'sub': {'registration_number': user_reg, 'user_type': self.user_type}
			}

			return jwt.encode(
				payload,
				SECRET_KEY,
				algorithm='HS256'
			)

		except Exception as e:
			return e

	@staticmethod
	def decode_auth_token(auth_token):
		"""
		Decodes the auth token
			:param auth_token:
			:return: integer|string
		"""
		
		try:
			payload = jwt.decode(auth_token, SECRET_KEY)
			return payload['sub']

		except jwt.ExpiredSignatureError:
			return 'Token expired. Please log in again.'

		except jwt.InvalidTokenError:
			return 'Invalid token. Please log in again.'


class UserSchema(ma.Schema):
	id = fields.Integer()
	first_name = fields.String(required=True, validate=validate.Length(1))
	middle_name = fields.String(required=True, validate=validate.Length(1))
	last_name = fields.String(required=True, validate=validate.Length(1))
	registration_number = fields.String(required=True, validate=validate.Length(equal=11))
	level = fields.String(validate=validate.Length(equal=3))
	faculty = fields.String(validate=validate.Length(1))
	department = fields.String(validate=validate.Length(1))
	institution = fields.String(validate=validate.Length(1))
	user_type = fields.String(required=True)
	roles = fields.List(fields.String(), required=True)
	created_at = fields.DateTime(dump_only=True)
