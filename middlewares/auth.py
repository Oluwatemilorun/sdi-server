import jwt
from functools import wraps
from flask import g, request, url_for, abort

from config import SECRET_KEY
from utils import response

from models.User import User, UserSchema

def check_auth(fn):
	"""
	Middleware decorator to check the authentication status of a user.

	`sdi_token` as key and a valid `JWT` as value must be available in `request.cookies`
	"""

	@wraps(fn)
	def check_auth_decorator(*args, **kwargs):

		# check if authentication token exist
		if 'sdi_token' in request.cookies:
			auth_token = request.cookies.get('sdi_token')

			# validate token
			try:
				payload = jwt.decode(auth_token, SECRET_KEY)
				payload = payload['sub']
				user = User.query.filter_by(
					registration_number=payload['registration_number'].replace('/', '_')
				).first()

				# check if user exist
				if not user:
					return response.error(
						message='Validation error. User not found',
						status=404
					)

				# make user available down pipline
				g.user_orm = user
				g.user = UserSchema().dump(user).data
				
				return fn(*args, **kwargs)

			except jwt.ExpiredSignatureError:
				return response.error(
					message='Token expired. Please log in again.',
					status=401
				)

			except jwt.InvalidTokenError:
				return response.error(
					message='Authentication failed. Please log in again.',
					status=401
				)

		else:
			return response.error(
				message='Empty token. Please log in again.',
				status=401
			)

	return check_auth_decorator
