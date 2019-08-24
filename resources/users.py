# this file contains logic resources for [/users, /users/<user_id>]

from flask import g, request, after_this_request
from flask_restful import Resource

from models.db import db
from models.User import User, UserSchema
from models.Assignment import Assignment, AssignmentSchema
from models.Submission import Submission

from middlewares.auth import check_auth
from middlewares.roles import validate_roles

from app import bcrypt
from utils import response

class AllUsers(Resource):
	"""
	All users resource. This resoucre is only available to users with roles `user_management`\n
	`GET` - Load all users in the database\n
	`POST` - Create a new user\n
	"""

	@check_auth
	@validate_roles(['admin', 'user_management'])
	def get(self):
		users = User.query.filter_by(is_active=True)
		users = UserSchema(many=True).dump(users).data
		
		return response.success(
			data=users,
			message='All users fetched'
		)

	@check_auth
	@validate_roles(['admin', 'user_management'])
	def post(self):
		req_data = request.get_json(force=True)
		if not req_data:
			return response.error(
				data='no input data provided',
				status=400
			)
		
		# validate and deserialize input
		# use this only when creating a new user
		data, errors = UserSchema().load(req_data)
		if errors:
			return response.error(
				data=errors,
				message='some required fields are missing',
				status=422
			)
		
		# check if user exist
		user = User.query.filter_by(
			registration_number=req_data['registration_number'].replace('/', '_').lower()
		).first()
		if user:
			return response.error(
				message='registration number already in use',
				status=400
			)

		try:
			user = User(
				first_name=req_data['first_name'],
				middle_name=req_data['middle_name'],
				last_name=req_data['last_name'],
				registration_number=req_data['registration_number'],
				level=req_data['level'],
				# faculty=req_data['faculty'],
				# department=req_data['department'],
				# institution=req_data['institution'],
				user_type=req_data['user_type'],
				roles=req_data['roles'],
				password=req_data['last_name'].upper() # use user's lastname as default password
			)

		except KeyError as err:
			return response.error(
				message='%s field is missing' % (err),
				status=422
			)

		db.session.add(user)
		db.session.commit()

		result = UserSchema().dump(user).data

		return response.success(
			message='user added successfully',
			data=result,
			status=200
		)


class SingleUser(Resource):
	"""
	Single user resource \n
	`GET` - load user profile of a single user :param user_reg: \n
	`PUT` - update information of a single user :param user_reg: \n
	`DELETE` - delete a single user from the database :param user_reg:
	"""

	@check_auth
	@validate_roles(['admin', 'user_management'])
	def get(self, user_reg):
		user = User.query.filter_by(registration_number=user_reg).first()

		if not user:
			return response.error(
				message='user not found',
				status=404
			)
		
		user = UserSchema().dump(user).data

		return response.success(
			data=user,
			message='users fetched'
		)


	@check_auth
	@validate_roles(['admin', 'user_management'])
	def put(self, user_reg):
		user = User.query.filter_by(registration_number=user_reg).first()

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
				message='user updated successfully',
				data=req_data,
				status=200
			)
			
		except Exception as e:
			print(e)
			return response.error(data=e)


	@check_auth
	@validate_roles(['admin', 'user_management'])
	def delete(self, user_reg):
		user = User.query.filter_by(registration_number=user_reg).first()

		if not user:
			return response.error(
				message='user not found',
				status=404
			)

		User.query.filter_by(registration_number=user_reg).delete()

		db.session.commit()

		return response.success(
			message='user deleted successfully',
			data={},
			status=200
		)


class ResetUserPassword(Resource):
	"""
	Generate password resource. For users who can't retreive their passwords \n
	`POST` - generate password of a single user :param user_reg: \n
	"""

	@check_auth
	@validate_roles(['admin', 'user_management'])
	def post(self, user_reg):
		user = User.query.filter_by(registration_number=user_reg).first()

		if not user:
			return response.error(
				message='user not found',
				status=404
			)

		user.password = user['last_name'].upper()
		db.session.commit()
		
		return response.success(
			message='user password generated successfully',
			data=user['last_name'],
			status=200
		)


class AddUserAssignment(Resource):
	"""
	A special case for carryover users. Adds an assignment to the user.\n
	`POST` - adds assignment to user :param user_reg:
	:body
	``` json
		{ "id": 1 }
	```
	"""

	@check_auth
	@validate_roles(['admin', 'user_management'])
	def post(self, user_reg):
		user = User.query.filter_by(registration_number=user_reg).first()

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

		try:
			assignment = Assignment.query.filter_by(id=req_data['id']).first()
		
		except KeyError as err:
			return response.error(
				message='%s field is missing' % (err),
				status=422
			)

		result = AssignmentSchema().dump(assignment).data
		user_dump = UserSchema().dump(user).data

		if result['level'] == user_dump['level']:
			return response.error(
				message='Cannot add assignment with level the same as user.',
				status=400
			)

		if req_data['id'] in user.co_assignments:
			return response.error(
				message='Assignment already exist for user.',
				status=400
			)

		new_assignments = []
		new_assignments.extend(user.co_assignments)
		new_assignments.append(req_data['id'])

		user.co_assignments = new_assignments
		db.session.commit()

		return response.success(
			message='assignment added for user successfully',
			data=result,
			status=200
		)


class Login(Resource):
	"""
	User Login Resource. \n
	`POST` - Login into sdi and receive authentication string to perform other operations
	:body
	``` json
		{ 
			"registration_number": "usr/12/1234",
			"password": "SURNAME"
		}
	"""
	
	def post(self):
		req_data = request.get_json(force=True)
		if not req_data:
			return response.error(
				data='no input data provided',
				status=400
			)

		if 'registration_number' and 'password' not in req_data:
			return response.error(
				data='registration_number/password required',
				status=400
			)
		
		try:
			user = User.query.filter_by(
				registration_number=req_data['registration_number'].replace('/', '_').lower()
			).first()

			# check if user exist
			if not user:
				return response.error(
					message='user not found',
					status=404
				)

			# check if password is correct
			if user.check_password(req_data['password']):
				auth_token = user.encode_auth_token(
					req_data['registration_number'].replace('/', '_').lower()
				)

				if auth_token:
					# execute function to set auth_token in cookies
					@after_this_request
					def set_auth_token(response):
						response.set_cookie(
							'sdi_token',
							auth_token.decode(),
							# max_age=648000,
							httponly=True
						)
						response.headers.set(
							'x-access-token',
							auth_token.decode(),
						)
						return response

					result = UserSchema().dump(user).data
					result['token'] = auth_token.decode()

					return response.success(
						data=result,
						message='log in successful'
					)
			
			else:
				return response.error(
					message='Invalid registration number or password',
					status=401
				)

		except Exception as e:
			print(e)

			return response.error(
				data=e
			)
