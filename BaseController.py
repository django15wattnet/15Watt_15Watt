from .Request import Request
from .Response import Response
from .Exceptions import Unauthorized


def decoratorLoginRequired(func):
	"""
		Decorator, der prüft, ob der Benutzer sich per BasicAuth angemeldet hat.
		Kann nur für AdmController-Methoden verwendet werden:
			def xAction(self, request: Request, response: Response):
	"""
	def wrapper(self, request: Request, response: Response):
		if 'Basic' != request.getEnvByKey('AUTH_TYPE'):
			response.stringContent = f"Invalid auth type: {request.getEnvByKey('AUTH_TYPE')}"
			response.returnCode = 401
			raise Unauthorized(response.stringContent)

		if request.getEnvByKey('REMOTE_USER') is None:
			response.stringContent = 'Unauthorized'
			response.returnCode = 401
			raise Unauthorized(response.stringContent)

		return func(self, request, response)
	return wrapper


class BaseController(object):
	"""
		Basisklasse aller AdmController
	"""
	def __init__(self, config: dict):
		self._config = config
