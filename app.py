from flask import Flask, Blueprint, request, jsonify, current_app, g
from flask_restful import Resource, Api
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# create flask app
app = Flask(__name__)

# use Werkzeug’s built-in password hashing utilities
bcrypt = Bcrypt(app)

# create flask blueprint
api_bp = Blueprint('api', __name__)

# allow CORS for all domains on all routes
CORS(app)

# use flask_restful resource routing
api = Api(api_bp)

from resources.users import AllUsers, SingleUser, ResetUserPassword, AddUserAssignment, Login
from resources.profile import Profile, LoadAssignments, LoadSingleAssignment
from resources.assignments import Assignments
from resources.project import AllProject

# setup the Api resource routing here
api.add_resource(Login, '/login')

api.add_resource(AllUsers, '/users')
api.add_resource(SingleUser, '/users/<user_reg>')
api.add_resource(ResetUserPassword, '/users/<user_reg>/reset-password')
api.add_resource(AddUserAssignment, '/users/<user_reg>/add-assignment')

api.add_resource(Profile, '/profile')
api.add_resource(LoadAssignments, '/profile/assignments')
api.add_resource(LoadSingleAssignment, '/profile/assignments/<ass_id>')

api.add_resource(Assignments, '/assignments')

api.add_resource(AllProject, '/projects')
