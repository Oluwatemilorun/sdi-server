
def parameterized(param):
	"""
	A decorator that allows function decorators accept parameters.
	
	Example usage
	``` python
	@parameterized
	def decorator (fn, param):
		def decorator_ (*xs, **kws):
			# ==== do something before fn
			return fn(*xs, **kws)
		return validate_roles_decorators
	```

	"""
	def layer(*args, **kwargs):
		def repl(fn):
			return param(fn, *args, **kwargs)
		return repl
	return layer
