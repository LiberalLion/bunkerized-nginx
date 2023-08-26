class ReverseProxied(object):

	def __init__(self, app):
		self.app = app

	def __call__(self, environ, start_response):
		if script_name := environ.get('HTTP_X_SCRIPT_NAME', ''):
			environ['SCRIPT_NAME'] = script_name
			path_info = environ['PATH_INFO']
			if path_info.startswith(script_name):
				environ['PATH_INFO'] = path_info[len(script_name):]

		if scheme := environ.get('HTTP_X_FORWARDED_PROTO', ''):
			environ['wsgi.url_scheme'] = scheme
		return self.app(environ, start_response)
