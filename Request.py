from typing import Dict
from urllib.parse import unquote, parse_qs
from io import BytesIO
from Wsgi.multipart import parse_form_data, MultipartPart
from .Exceptions import ParamNotFound, ValueNotFound, FileNotFound


class Request(object):
	"""
		Abbildung des Requests
	"""
	def __init__(self, env: dict, paramsFromRoute: dict):
		self.__env      = env
		self.__header   = {}
		self.__user     = self.__user = env.get('REMOTE_USER', '')
		self.__password = ''

		self.__params, self.__files = self.__getParameters(env, paramsFromRoute)

		self.__requestBodySize = 0
		self.__requestBody     = ''

		try:
			self.__requestBodySize = int(self.__env.get('CONTENT_LENGTH', 0))
		except ValueError:
			pass
		except TypeError:
			pass

		byteIo = BytesIO(initial_bytes=env['wsgi.input'].read(self.__requestBodySize))

		# Read the requests body no matter what content type or method the request is
		byteIo.seek(0)
		self.__requestBody = unquote(byteIo.read(self.__requestBodySize).decode('utf-8'))
		byteIo.close()

		# Methode
		self.__requestMethod = self.__env.get('REQUEST_METHOD', 'GET')

		return


	def getRequestBody(self) -> str:
		return self.__requestBody


	def get(self, name: str):
		"""
			Liefert den Parameter name.
			Gibt es mehrere Werte mit dem Namen, wird der erste Wert geliefert.
		:raise: ParamNotFound
		"""
		if name not in self.__params:
			raise ParamNotFound(f'Parameter {name} not found')

		if 0 == len(self.__params[name]):
			raise ParamNotFound(f'Parameter {name} is empty')

		return self.__params[name][0]


	def getAsList(self, name: str) -> list:
		"""
			Liefert die Liste der Werte des Parameters name
		:raise: ParamNotFound
		"""
		if name not in self.__params:
			raise ParamNotFound(f'Parameter {name} not found')

		if 0 == len(self.__params[name]):
			raise ParamNotFound(f'Parameter {name} is empty')

		return self.__params[name]


	def getDictParams(self) -> dict:
		"""
			Liefert die Parameter als Dict
		:return:
		"""
		return self.__params


	def has(self, name: str):
		"""
			Prüft, ob es den Parameter name gibt
		:param name:
		:return: bool
		"""
		return name in self.__params


	def hasFile(self, name: str):
		"""
			Prüft, ob es für name eine Datei gibt
		:param name:
		:return:
		"""
		return name in self.__files


	def getFile(self, name: str) -> MultipartPart:
		"""
			Liefert die Datei zu name
		:raise: ParamNotFound
		"""
		if name not in self.__files:
			raise FileNotFound(f'File {name} not found')

		return self.__files[name]


	def getDíctFiles(self) -> Dict[str, MultipartPart]:
		"""
			Liefert die Dateien als Dict
		:return:
		"""
		return self.__files


	def getHeader(self, name: str):
		"""
			Liefert das Header-Value zu name
		:param name:
		:return:
		:raise: ValueNotFound
		"""
		if name not in self.__header:
			raise ValueNotFound(f'Header-Field {name} not found')

		return self.__header[name]


	def hasHeader(self, name: str):
		"""
			Prüft, ob es für name einen Wert in den Header-Values gibt
		:param name:
		:return:
		"""
		return name in self.__header


	def envHasKey(self, key: str) -> bool:
		"""
			Prüft, ob es für key einen Wert in den env-Values gibt
		"""
		return key in self.__env


	def getEnvByKey(self, key: str) -> str|None:
		"""
			Liefert den Wert zu key aus dem env-Dict oder None
		"""
		return self.__env.get(key, None)


	@property
	def env(self) -> dict:
		"""
			Liefert das env-Dict
		"""
		return self.__env


	def __getParameters(self, env: dict, paramsFromRoute: dict) -> (dict, dict):
		"""
			Reads the parameters from all sources:
				- from the query string (GET)
				- from the request body (POST, PUT)
				- from the path (Route)

			Each parameter can have multiple values.
			Files will be stored as a parameter und in
		"""
		dictParams = {}
		dictFiles  = {}

		# Die Parameter aus der Route hinzufügen
		for key in paramsFromRoute:
			dictParams[key] = [paramsFromRoute[key]]
			print((paramsFromRoute[key]))

		# Die Parameter aus dem Query-String hinzufügen
		queryParams = parse_qs(env.get('QUERY_STRING', ''))
		for item in queryParams.items():
			if item[0] in dictParams:
				dictParams[item[0]] += item[1]
			else:
				dictParams[item[0]] = item[1]

		# Die Parameter aus dem Body hinzufügen
		(dictForm, dictMultiFiles) = parse_form_data(environ=env)

		for key in dictForm:

			if key in dictParams:
				dictParams[key] += [dictForm[key]]
			else:
				dictParams[key] = [dictForm[key]]


		for key in dictMultiFiles:
			if key in dictParams:
				dictParams[key] += [dictMultiFiles[key]]
			else:
				dictParams[key] = [dictMultiFiles[key]]

			# Save files separately
			dictFiles[key] = dictMultiFiles[key]

		return dictParams, dictFiles
