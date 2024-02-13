import traceback
from importlib import import_module
from importlib.resources import path

from sqlobject import *
from .Request import Request
from .Response import Response
from .Route import Route, HttpMethods


class Kernel(object):
	"""
		Handles the complete request to response cycle.
	"""
	def __init__(self):
		self.__routes = {}
		self.__config = {}
		self.__env    = {}
		self.__loadConfig()
		self.__connectToDatabase()
		self.__loadRoutes()


	def run(self, env: dict, startResponse):
		"""
			Handles to whole request
		"""
		self.__env = env

		# Find the controller and method, for a route without parameters
		keyRoute = env.get('REQUEST_METHOD') + '_' + env.get('PATH_INFO')

		if keyRoute in self.__routes:
			# Found, so I call the controller method
			# Create a request instance
			request = Request(env=env)

			# Create a response instance
			response = Response(
				startResponse=startResponse,
				request=request
			)

			try:
				self.__addAccessControlHeader(request=request, response=response)

				self.__routes[keyRoute].methodToCall(
					request=request,
					response=response
				)
			except Exception as e:
				if 'debug' in self.__config and self.__config['debug'] is True:
					tb = traceback.format_exc()
				else:
					tb = ''

				response.returnCode = 500
				response.stringContent = 'Internal server error.\n{tb}'.format(tb=tb)
				response.contentType = 'text/plain'
				response.charset = 'utf-8'

			return response.getContent()

		# It has to be a route with parameters
		# Iterate over all routes
		for idx in self.__routes:
			if self.__routes[idx].match(path=env.get('PATH_INFO'), httpMethod=HttpMethods[env.get('REQUEST_METHOD')]):
				request = Request(
					env=env,
					paramsFromRoute=self.__routes[idx].getParamsFromPath(path=env.get('PATH_INFO'))
				)
				response = Response(
					startResponse=startResponse,
					request=request
				)

				# Call the controller method
				try:
					self.__routes[idx].methodToCall(
						request=request,
						response=response
					)

					self.__addAccessControlHeader(request=request, response=response)

				except Exception as e:
					if 'debug' in self.__config and self.__config['debug'] is True:
						tb = traceback.format_exc()
					else:
						tb = ''

					response.returnCode = 500
					response.stringContent = f'Internal server error.\n{tb}'
					response.contentType = 'text/plain'
					response.charset = 'utf-8'

				return response.getContent()


		# No matching route found
		# todo Error-Controller erstellen
		request = Request(env=env)
		response = Response(
			startResponse=startResponse,
			request=request
		)

		response.returnCode    = 404
		response.stringContent = f'No controller method found for route: {keyRoute}'
		response.contentType   = 'text/plain'
		response.charset       = 'utf-8'

		return response.getContent()


	def __loadConfig(self):
		"""
			Reads the variables from project root.config.py
		:return:
		"""
		config = import_module(name='config')
		for k in dir(config):
			if k.startswith('__'):
				continue

			self.__config[k] = getattr(config, k)

		return


	def __connectToDatabase(self):
		"""
			If the key uriDb is present in the config, a database connection
			will be established.
		:return:
		"""
		if 'uriDb' not in self.__config:
			self.__config['dbConnection'] = None
			return

		self.__config['dbConnection'] = connectionForURI(uri=self.__config['uriDb'])
		sqlhub.processConnection = self.__config['dbConnection']


	def __loadRoutes(self):
		"""
			Loads all routes and injects the configuration to them
		:return:
		"""
		module = import_module(name='routes')
		for route in getattr(module, 'routes'):
			route.setConfig(config=self.__config)
			k = route.httpMethod.name + '_' + route.pathRegEx
			self.__routes[k] = route


	def __addAccessControlHeader(self, request: Request, response: Response):
		if 'accessControlAllowOrigin' not in self.__config:
			return

		accessControlAllowOrigin = []
		accessControlAllowOrigin = accessControlAllowOrigin + self.__config['accessControlAllowOrigin']

		if 0 == len(accessControlAllowOrigin) or False == request.hasHeader('Origin'):
			return

		for url in accessControlAllowOrigin:
			if request.getHeader('Origin') == url:
				response.addHeader('Access-Control-Allow-Origin', url)


	def __str__(self):
		"""
			Just a dump string representation of the kernel
		"""
		ret = 'Config:\n'
		for k in self.__config:
			ret += '\t{key}={val}\n'.format(key=k, val=self.__config[k])

		ret += '\nRoutes:\n'

		for k in self.__routes:
			ret += '\t' + str(self.__routes[k]) + '\n'

		ret += '\nENV:\n'

		for k in self.__env:
			ret += '\t{key}={val}\n'.format(key=k, val=self.__env[k])

		return ret
