from cgi import FieldStorage
from urllib.parse import unquote
from io import BytesIO

from .Exceptions import ParamNotFound, ValueNotFound
from .Route import Route


class Request(object):
	"""
		Abbildung des Requests
	"""
	def __init__(self, env: dict, paramsFromRoute: dict = {}):
		self.__env    = env
		self.__header = {}
		self.__params = {}

		self.__requestBodySize = 0
		self.__requestBody = ''
		try:
			self.__requestBodySize = int(self.__env.get('CONTENT_LENGTH', 0))
		except ValueError:
			pass
		except TypeError:
			pass

		byteIo = BytesIO(initial_bytes=env['wsgi.input'].read(self.__requestBodySize))

		# Content-Type ermitteln
		if 'CONTENT_TYPE' in env:
			if env['CONTENT_TYPE'].startswith('multipart/form-data'):
				self.__contentType = 'multipart/form-data'
			else:
				self.__contentType = env['CONTENT_TYPE']
		else:
			self.__contentType = ''

		# Soll sich FieldStorage komplett ums Parsen kümmern
		if self.__contentType.split(';')[0] in ['multipart/form-data', 'application/x-www-form-urlencoded']:
			self.__getHeaderAndParamsFromFieldStorage(
				self.__env,
				FieldStorage(fp=byteIo, environ=env, keep_blank_values=True)
			)

			# todo: Lesen des Bodys sauber umsetzen
			if self.__requestBodySize > 0:
				byteIo.seek(0)
				self.__requestBody = byteIo.read(self.__requestBodySize)
		else:
			self.__fillByOwnBodyParse(byteIo)

		# Read the requests body no matter what content type or method the request is
		# byteIo.seek(0)
		# self.__requestBody = unquote(byteIo.read(self.__requestBodySize).decode('utf-8'))

		# Methode
		self.__requestMethod = self.__env.get('REQUEST_METHOD', 'GET')

		byteIo.close()

		# Die Parameter aus der Route hinzufügen
		for key in paramsFromRoute:
			self.__params[key] = paramsFromRoute[key]

		return


	def getRequestBody(self):
		return self.__requestBody


	def get(self, name: str):
		"""
			Liefert den Parameter name.
			Gibt es mehrere Werte mit dem Namen, wird der erste Wert geliefert.
		:param name:
		:param name:
		:return:
		:raise: ParamNotFound
		"""
		if name not in self.__params:
			raise ParamNotFound('Parameter {name} not found'.format(name=name))

		if type(self.__params[name]) is list:
			return self.__params[name][0].value

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


	def getHeader(self, name: str):
		"""
			Liefert das Header-Value zu name
		:param name:
		:return:
		:raise: ValueNotFound
		"""
		if name not in self.__header:
			raise ValueNotFound('Header-Field {name} not found'.format(name=name))

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


	# todo seek(0) einbauen unquote einbauen


	def __fillByOwnBodyParse(self, byteIo):
		"""
			Der Content-Type kann nicht von FieldStorage verarbeitet werden.
		:return:
		"""
		# Zuerst den Body selbst auslesen
		if self.__requestBodySize > 0:
			self.__requestBody = byteIo.read(self.__requestBodySize)

		env = self.__env.copy()
		env['CONTENT_LENGTH'] = 0
		env['CONTENT_TYPE']   = 'application/x-www-form-urlencoded'

		byteIo.seek(0)
		self.__getHeaderAndParamsFromFieldStorage(
			env=env,
			fieldStorage=FieldStorage(fp=byteIo, environ=env, keep_blank_values=True)
		)

		return


	def __getHeaderAndParamsFromFieldStorage(self, env: dict, fieldStorage: FieldStorage):
		"""
			Liest aus der FieldStorage die Header- und Parameterwerte.
		:param fieldStorage:
		:return:
		"""
		for key, val in env.items():
			self.__header[key] = val

		for key in fieldStorage:
			s = fieldStorage[key]

			if type(s) is list:
				self.__params[key] = s
				continue

			self.__params[key] = s.value

		return
