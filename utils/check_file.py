import config

def allowed_file(filename):
	file_extn = filename.rsplit('.', 1)[1].lower()

	allowed = True if file_extn in config.ALLOWED_EXTENSIONS else False
	
	return file_extn, allowed