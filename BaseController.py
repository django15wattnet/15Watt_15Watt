class BaseController(object):
	"""
		Basisklasse aller Controller
	"""
	def __init__(self, config: dict):
		self._config = config
