import config

def allowed_file(filename):
	if '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS:
		file_extn = filename.rsplit('.', 1)[1].lower()
		allowed = True

	else:
		file_extn: None
		allowed = False

	return {"extension": file_extn, "allowed": allowed}