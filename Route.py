from enum import Enum
from importlib import import_module
import re
from .Exceptions import NotAllowedHttpMethod, InvalidData


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
    def __init__(
            self,
            path: str,
            nameController: str,
            nameMethod: str,
            httpMethod: HttpMethods,
            paramsDef: dict = {}
    ):

        if httpMethod not in HttpMethods:
            raise NotAllowedHttpMethod(httpMethod)

        self.__path                = path
        self.__nameControllerParts = nameController.split('.')
        self.__nameMethod          = nameMethod
        self.__methodToCall        = None
        self.__httpMethod          = httpMethod
        self.__dictParamsDef       = paramsDef
        self.__pathRegEx           = self.__buildPathRegEx()
        self.__config              = {}


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


    @property
    def pathRegEx(self):
        return self.__pathRegEx


    def setConfig(self, config: dict):
        self.__config = config


    def match(self, path: str, httpMethod: HttpMethods) -> bool:
        if httpMethod != self.__httpMethod:
            return False

        return re.match(f'^{self.__pathRegEx}$', path) is not None


    def getParamsFromPath(self, path: str) -> dict:
        """
            Liefert die Parameter aus dem Pfad
        """
        matches = re.match(self.__pathRegEx, path)
        if matches is None:
            return {}

        paramsFromPath = {}
        for placeHolder in self.__dictParamsDef:
            if 'str' == self.__dictParamsDef[placeHolder]:
                paramsFromPath[placeHolder] = matches.group(placeHolder)
            elif 'int' == self.__dictParamsDef[placeHolder]:
                paramsFromPath[placeHolder] = int(matches.group(placeHolder))

        return paramsFromPath


    def __buildMethod(self):
        nameModule = '.'.join(self.__nameControllerParts[:-1])
        nameClass  = self.__nameControllerParts[-1]
        module     = import_module(name=nameModule)
        # todo inject Request, Response
        inst       = getattr(module, nameClass)(config=self.__config)
        return getattr(inst, self.__nameMethod)


    def __buildPathRegEx(self):
        """
            Baut den RegEx-String zum matchen der Route
        """
        strPathRegEx = self.__path

        for placeHolder in re.findall(r'\{[\w]{1,}\}', strPathRegEx):
            placeHolderPlain = placeHolder.strip('{}')

            if placeHolderPlain not in self.__dictParamsDef:
                raise InvalidData(f'Parameter "{placeHolderPlain}" not defined in paramsDef. Route = {self.__path}')

            if 'str' == self.__dictParamsDef[placeHolderPlain]:
                to = "(?P<{n}>\\w{{1,}})".format(n=placeHolderPlain)
            elif 'int' == self.__dictParamsDef[placeHolderPlain]:
                to = "(?P<{n}>[0-9]{{1,}})".format(n=placeHolderPlain)
            else:
                raise InvalidData(f'Not allowed data type: {self.__dictParamsDef[placeHolderPlain]}')

            strPathRegEx = strPathRegEx.replace(placeHolder, to)

        return strPathRegEx


    def __str__(self):
        return 'Path={path} {httpMethod} {controller}.{method}'\
            .format(
                path=self.__path,
                httpMethod=self.__httpMethod.name,
                controller='.'.join(self.__nameControllerParts),
                method=self.__nameMethod
            )
