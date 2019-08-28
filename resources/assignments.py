# this file contains logic for [/projects, /project/<project_id>]

import os, config
from flask import g, request
from flask_restful import Resource
from werkzeug.utils import secure_filename

from models.db import db
from models.Assignment import Assignment, AssignmentSchema
from models.User import User, UserSchema
from models.Layer import Layer, LayerSchema

from middlewares.auth import check_auth
from middlewares.roles import validate_roles

from utils import response, check_file, zip_files, layer_processing

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
				instruction=req_data['instruction'],
				course_code=req_data['course_code'],
				level=req_data['level'],
				date_end=req_data['date_end'],
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


class SingleAssignment(Resource):

	@check_auth
	@validate_roles(['admin', 'assignment_management'])
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

		result = AssignmentSchema().dump(assignment).data
		result['layers'] = LayerSchema(many=True).dump(assignment.layers).data

		return response.success(
			data=result,
			message='Assignment fetched'
		)

	@check_auth
	@validate_roles(['admin', 'assignment_management'])
	def put(self, ass_id):
		assignment = Assignment.query.filter_by(id=ass_id, is_active=True).first()

		if not assignment:
			return response.error(
				message='assignment not found',
				status=404
			)

		req_data = request.get_json(force=True)
		if not req_data:
			return response.error(
				data='no input data provided',
				status=400
			)

		blacklist = ['supervisors', 'submissions',
                    'created_at', 'db_name', 'db_username', 'db_password']

		try:
			for key in req_data:
				if req_data[key] and key not in blacklist:
					setattr(assignment, key, req_data[key])

		except Exception as e:
			print(e)
			return response.error(data=e)
		
					
		db.session.commit()
		result = AssignmentSchema().dump(assignment).data

		return response.success(
			message='assignment updated successfully',
			data=result,
			status=200
		)


class AddAssignmentData(Resource):

	@check_auth
	@validate_roles(['admin', 'assignment_management'])
	def post(self, ass_id):

		assignment = Assignment.query.filter_by(id=ass_id, is_active=True).first()

		if not assignment:
			return response.error(
				data='Assignment no found',
				status=404
			)

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
		
		assignment = AssignmentSchema().dump(assignment).data

		try:
			os.chmod(os.path.join(config.UPLOAD_FOLDER), 0o777)

			if os.path.exists(os.path.join(config.UPLOAD_FOLDER, assignment['db_name'])):
				pass

			else:
				os.makedirs(os.path.join(config.UPLOAD_FOLDER, assignment['db_name']))

			filename = secure_filename(file.filename)
			file.save(os.path.join(config.UPLOAD_FOLDER, assignment['db_name'], filename))
			
		except Exception as e:
			print(e)
			response.error(data=e)

		if extension == 'zip':
			extracted_files = zip_files.extract_zip(
				os.path.join(config.UPLOAD_FOLDER, assignment['db_name'], filename),
				os.path.join(config.UPLOAD_FOLDER, assignment['db_name'])
			)
					
			return response.success(
				data=extracted_files,
				message='FIle uploaded successfully'
			)
			
		else:
			return response.success(
				data=filename,
				message='FIle uploaded successfully'
			)
			
			

class SaveAssignmentData(Resource):


	@check_auth
	@validate_roles(['admin', 'assignment_management'])
	def post(self, ass_id):
		req_data = request.get_json(force=True)
		if not req_data:
			return response.error(
				message='no input data provided',
				status=400
			)
		
		assignment = Assignment.query.filter_by(id=ass_id, is_active=True).first()

		if not assignment:
			return response.error(
				message='Assignment not found',
				status=404
			)
			
		assignment = AssignmentSchema().dump(assignment).data

		uploaded_files = req_data['files']

		for file in uploaded_files:
			if os.path.exists(os.path.join(config.UPLOAD_FOLDER, assignment['db_name'], file)):
				pass
			else:
				return response.error(
					message='<%s> file has not been uploaded or deleted. Please upload file again.' % (file),
					status=422
				)

		database = {"user": assignment['db_username'],
						"pass": assignment['db_password'],
						"name": assignment['db_name']}

		def add_layer_to_db (filename):
			'''
			Save layer record to db.\n
			:params :filename: -> LayerData
			'''
			layer = Layer.query.filter_by(assignment_id=ass_id, filename=filename, layer_type=req_data['data_type'], is_active=True).first()
			if not layer:
				layer = Layer(
					filename=filename,
					layer_type=req_data['data_type'],
					database=assignment['db_name'],
					assignment_id=assignment['id'],
					project_id=None
				)

				db.session.add(layer)
				db.session.commit()

			return LayerSchema().dump(layer).data

		
		# validation for ESRI shapefile
		if req_data['data_type'] == 'shapefile':
			# TODO: create instance for where there are more than one shapefile
			
			shp_file = [y for y in uploaded_files if y.find('.shp') != -1]
			shp_file = shp_file[0].rsplit('.shp')[0] if shp_file.__len__() >= 1 else None

			if not shp_file:
				return response.error(
					message='Error proccessing uploaded files for format shapefile. Cannot find <.shp> file.',
					status=422
				)
			
			required_formats = ['%s.shp' % (shp_file), '%s.shx' % (shp_file), '%s.dbf' % (shp_file)]
			for r_format in required_formats:
				if r_format not in uploaded_files:
					return response.error(
						message='Error proccessing uploaded files for format shapefile. Required file <%s> missing.' % (r_format),
						status=422
					)

			# process shapefile
			processing_state, processing_message = layer_processing.save_shapefile_layer('%s.shp' % (shp_file), database)

			if processing_state:
				# save layer record to db
				layerRes = add_layer_to_db(shp_file)

				return response.success(
					data=layerRes,
					message="Data/Layer processed and added successfully"
				)

			else:
				return response.error(
					message=processing_message,
					status=422
				)

		# TODO: test this
		elif req_data['data_type'] == 'csv':
			for file in uploaded_files:
				processing_state, processing_message = layer_processing.save_shapefile_layer(file, database)
				if not processing_state:
					return response.error(
						message=processing_message,
						status=422
					)

				# save layer record to db
				layerRes = add_layer_to_db(file.rsplit('.')[0].lower())
				
			return response.success(
				data=layerRes,
				message="Data/Layer processed and added successfully"
			)

		elif req_data['data_type'] == 'raster':
			layerRes = []
			for file in uploaded_files:
				processing_state, processing_message = layer_processing.save_raster_layer(file, database)

				if not processing_state:
					return response.error(
						message=processing_message,
						status=422
					)

				# save layer record to db
				layerRes.append(add_layer_to_db(file.rsplit('.')[0].lower()))
				
			return response.success(
				data=layerRes,
				message="Data/Layer processed and added successfully"
			)


