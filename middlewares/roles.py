from functools import wraps
from flask import g, request, url_for

from config import SECRET_KEY
from utils import response, decorators

@decorators.parameterized
def validate_roles (fn, roles):
	"""
	Middleware decorator to validate the role of the user\n
		:param roles:list `roles the user most fulfil`

	Available types: 
	`user_management` | `project_management` | `assignment_management` | `default`
	"""

	def validate_roles_decorator (*xs, **kws):
		for role in roles:
			if role in g.user['roles']:
				return fn(*xs, **kws)
			
			else:
				return response.error(
					message='You don\'t have access to perform this action.',
					status=401
				)

	return validate_roles_decorator
