# this file contains logic for [/projects, /project/<project_id>]

import os, config
from flask import g, request
from flask_restful import Resource
from werkzeug.utils import secure_filename

from models.db import db
from models.Assignment import Assignment, AssignmentSchema
from models.User import User, UserSchema

from middlewares.auth import check_auth
from middlewares.roles import validate_roles

from utils import response, check_file

class Assignments(Resource):
	"""
	Get and create assignments resource.\n
	`GET` - Load all available assignments in the database\n
	`POST` - Create a new assignments. Requires `assignment_management` role\n
	"""

	@check_auth
	@validate_roles(['admin', 'assignment_management'])
	def post(self):
		req_data = request.get_json(force=True)
		if not req_data:
			return response.error(
				data='no input data provided',
				status=400
			)

		# validate and deserialize input
		# use this only when creating a new assignments
		data, errors = AssignmentSchema().load(req_data)
		if errors:
			return response.error(
				data=errors,
				message='some required fields are missing',
				status=422
			)

		# load all available users in level and add them as participant
		# participants = User.query.filter_by(level=data['level'], is_active=True)
		# participants = UserSchema(many=True).dump(participants).data
		# participants = [a['id'] for a in participants]
		
		# if participants.__len__() == 0:
		# 	return response.error(
		# 		data=[],
		# 		message='No student(s) in [%s] level. Can\'t create assignment with no participant.' % (
		# 			req_data['level']
		# 		),
		# 		status=422
		# 	)

		try:
			assignment = Assignment(
				name=req_data['name'],
				instruction=req_data['instructions'],
				level=req_data['level'],
				db_name=g.user['last_name'].lower(),
				db_username=g.user['registration_number'], # use users reg_number as default db username
				db_password=g.user['last_name'], # use users lastname as default db password
				user_id=g.user['id'],
				supervisors=[g.user['id']],
				# participant=participants
			)

		except KeyError as err:
			return response.error(
				message='%s field is missing' % (err),
				status=422
			)
		
		db.session.add(assignment)
		db.session.commit()

		result = AssignmentSchema().dump(assignment).data

		return response.success(
			message='assignment created successfully',
			data=result,
			status=200
		)
	
	@check_auth
	@validate_roles(['admin', 'assignment_management'])
	def get(self):
		assignments = Assignment.query.filter_by(is_active=True)

		result = AssignmentSchema(many=True).dump(assignments).data
		return response.success(
			data=result,
			message="All assignments fetched successfully"
		)


class AddAssignmentData(Resource):

	@check_auth
	@validate_roles(['admin', 'assignment_management'])
	def post(self, ass_id):

		if 'file' not in request.files:
			return response.error(
				data='no file part provided',
				status=422
			)
		
		file = request.files['file']

		if file and file.filename == '':
			return response.error(
				data='no input file provided',
				status=400
			)

		extension, allowed = check_file.allowed_file(file.filename)

		if not allowed:
			return response.error(
				data='file with extension <%s> not allowed' % (extension),
				status=422
			)

		assignment = Assignment.query.filter_by(id=ass_id, is_active=True)

		try:
			os.makedirs(os.path.join(config.UPLOAD_FOLDER, assignment['db_name']))

		except FileExistError:
			pass
			
		filename = secure_filename(file.filename)
		file.save(os.path.join(config.UPLOAD_FOLDER, assignment['db_name'], filename))

