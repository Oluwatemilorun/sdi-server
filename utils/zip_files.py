import zipfile

def check_zip(file):
	return True if zipfile._check_zipfile(file) else False

def extract_zip(file, destination):
	"""
	Using the `zipfile` module to extract files from a zip

		:params :file: path to the file you want to extract
		:params :destination: path to the directory files will be extracted in
	"""
	with zipfile.ZipFile(file) as zip_ref:
		files = zip_ref.namelist()
		zip_ref.extractall(destination)
		return files

def compress_zip():
	with zipfile as zip_ref:
		pass	