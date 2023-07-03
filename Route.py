
from enum import Enum
from importlib import import_module

from Wsgi.Exceptions import NotAllowedHttpMethod


class HttpMethods(Enum):
    """
        Die erlaubten HTTP-Methoden
    """
    GET      = 1
    POST     = 2
    PUT      = 3
    PATCH    = 4
    DELETE   = 5
    COPY     = 6
    HEAD     = 7
    OPTIONS  = 8
    LINK     = 9
    UNLINK   = 10
    PURGE    = 11
    LOCK     = 12
    PROPFIND = 13
    VIEW     = 14


class Route(object):
    """
        Verknüpfung zwischen Pfad und Controller-Methode
        todo Routen mit Parametern ermöglichen. Siehe: regExe_fuer_routen_mit_parametern.py
    """
    # Die Konfiguration als Key/Value-Paare
    __config = {}


    def __init__(self, path: str, nameController: str, nameMethod: str, httpMethod: HttpMethods):
        if httpMethod not in HttpMethods:
            raise NotAllowedHttpMethod(httpMethod)

        self.__path                = path
        self.__nameControllerParts = nameController.split('.')
        self.__nameMethod          = nameMethod
        self.__methodToCall        = None
        self.__httpMethod          = httpMethod


    @property
    def path(self):
        return self.__path


    @property
    def methodToCall(self):
        if self.__methodToCall is None:
            self.__methodToCall = self.__buildMethod()

        return self.__methodToCall


    @property
    def httpMethod(self):
        """

        :return: HttpMethods
        """
        return self.__httpMethod


    def setConfig(self, config: dict):
        self.__config = config


    def __buildMethod(self):
        nameModule = '.'.join(self.__nameControllerParts[:-1])
        nameClass  = self.__nameControllerParts[-1]
        module     = import_module(name=nameModule)
        # todo inject Request, Response
        inst       = getattr(module, nameClass)(config=self.__config)
        return getattr(inst, self.__nameMethod)


    def __str__(self):
        return 'Path={path} {httpMethod} {controller}.{method}'\
            .format(
                path=self.__path,
                httpMethod=self.__httpMethod.name,
                controller='.'.join(self.__nameControllerParts),
                method=self.__nameMethod
            )
