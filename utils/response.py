
def success(data, message="operation successful", status=200):
	"""
	Formated success response method for easy access
		:return: object, int
	"""

	return {
		'message': message,
		'data': data,
		'status': status
	}, status

def error(data=[], message="Error occured. Try again later", status=500):
	"""
	Formated error response method for easy access
		:return: object, int
	"""
	
	return {
		'data': data,
		'message': message,
		'status': status
	}, status
