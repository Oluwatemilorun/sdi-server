'Database model for all layers'

from marshmallow import Schema, fields, validate
from flask_marshmallow import Marshmallow

from .db import db
from .Assignment import AssignmentSchema

ma = Marshmallow()

class Layer(db.Model):
	"""
	Layer model for keeping records of all layers added to the SDI
	"""
	__tablename__ = 'layers'

	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(100), nullable=False)
	layer_type = db.Column(db.String(20), nullable=False)
	database = db.Column(db.String(30), nullable=False)

	assignment_id = db.Column(db.Integer(), db.ForeignKey('assignments.id'))
	project_id = db.Column(db.Integer(), db.ForeignKey('projects.id'))

	is_active = db.Column(db.Boolean, default=True, nullable=False)

	created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

	def __init__(
		self,
		filename,
		layer_type,
		database,
		assignment_id,
		project_id
	):
		self.filename = filename
		self.layer_type = layer_type
		self.database = database
		self.assignment_id = assignment_id
		self.project_id = project_id

		self.is_active = True


class LayerSchema(Schema):
	id = fields.Integer()
	filename = fields.String(required=True)
	layer_type = fields.String(required=True)
	database = fields.String(required=True)

	created_at = fields.DateTime(dump_only=True)

	assignment = fields.Nested(AssignmentSchema, only=['id', 'name', 'course_code', 'level'])
