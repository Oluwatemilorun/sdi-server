# This file contains user resources for an authenticated user ['/profile']

from flask import g, request, after_this_request
from flask_restful import Resource

from models.db import db
from models.User import User, UserSchema
from models.Assignment import Assignment, AssignmentSchema
from models.Layer import Layer, LayerSchema

from middlewares.auth import check_auth
from middlewares.roles import validate_roles

from app import bcrypt
from utils import response

class Profile(Resource):
	"""
	Current authenticated user `g.user` profile resource.\n
	`GET` - Load the user's profile.\n
	`PUT` - Update the user's profile
	"""

	@check_auth
	def get(self):
		user = g.user

		return response.success(
			data=user,
			message='profile loaded'
		)

	@check_auth
	def put(self):
		user = User.query.filter_by(
			registration_number=g.user['registration_number']
		).first()

		if not user:
			return response.error(
				message='user not found',
				status=404
			)

		req_data = request.get_json(force=True)
		if not req_data:
			return response.error(
				data='no input data provided',
				status=400
			)

		blacklist = ['password', 'roles', 'user_type',
                    'is_active', 'projects', 'created_at', 'registration_number']

		try:
			for key in req_data:
				if req_data[key] and key not in blacklist:
					setattr(user, key, req_data[key])

			db.session.commit()

			return response.success(
				message='profile updated successfully',
				data=req_data,
				status=200
			)

		except Exception as e:
			print(e)
			return response.error(data=e)


class LoadAssignments(Resource):
	"""
	Authenticated user assignment resource.
	Performs a check on the `user_type` to the user and uses that to know how to load the assignments.\n
	If `user_type == 'student'` the assignments will be loaded using the `level` query. \n
	If `user_type == 'lecturer' or 'technician' or 'supervisor'` the assignment will be loaded
	from `User.assignments`  \n
	`GET` - Load all available assignments for logged user `g.user` in the database\n
	"""

	@check_auth
	def get(self):
		registration_number = g.user['registration_number']
		user_type = g.user['user_type']
		user = User.query.filter_by(
			registration_number=registration_number,
			is_active=True
		).first()

		if user_type == 'student':
			# use this when you need to join `Relationships`
			assignments = db.session.query(Assignment).join(User).filter(
				Assignment.level == g.user['level'],
				Assignment.is_active == True
			).all()

			assignments = AssignmentSchema(many=True).dump(assignments).data
			co_assignments = user.co_assignments
			
			for id in co_assignments:
				co_assignment = Assignment.query.filter_by(id=id).first()
				if not co_assignment: continue
				else: assignments.append(AssignmentSchema().dump(co_assignment).data)


		else:
			# TODO:
			# do a search for through assignments and load the supervisors
			assignments = user.assignments
			assignments = AssignmentSchema(many=True).dump(assignments).data
		
			# assignments = user.assignments
		# assignments = AssignmentSchema(many=True).dump(assignments).data

		return response.success(
			message='assignments retrieved successfully',
			data=assignments,
			status=200
		)


class LoadSingleAssignment(Resource):

	@check_auth
	def get(self, ass_id):
		assignment = db.session.query(Assignment).join(User).filter(
			Assignment.id == ass_id,
			Assignment.is_active == True
		).first()
		
		if not assignment:
			return response.error(
				message='Assignment not found',
				status=404
			)

		if g.user['user_type'] == 'student':
			if assignment['level'] == g.user['level'] or assignment['id'] in g.user['co_assignments']:
				pass

			else:
				return response.error(
					message='This assignment is not assigned to you.',
					status=404
				)
		
		result = AssignmentSchema().dump(assignment).data
		result['layers'] = LayerSchema(many=True).dump(assignment.layers).data
		
		return response.success(
			data=result,
			message='Assignment fetched'
		)
