# this file contains logic for [/projects, /project/<project_id>]

from flask_restful import Resource
from models.db import db
from models.Project import Project

class AllProject(Resource):
	def get(self):

		return {}

	def post(self):

		return {}
