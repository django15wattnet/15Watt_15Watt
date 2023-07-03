from .Request import Request
from .Exceptions import NotAllowedHttpResponseCode
from .Cookie import Cookie


class ResponseCodeToText(object):
    """
        Translates the web servers numeric response code to its
        string representation:
        200 -> 200 OK
        401 -> Unauthorized
        ...
    """
    __numToTxt = {
        100: 'Continue',
        101: 'Switching Protocols',
        102: 'Processing',
        103: 'Early Hints',

        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non - Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        207: 'Multi - Status',
        208: 'Already Reported',
        226: 'IM Used',

        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        307: 'Temporary Redirect',
        308: 'Permanent Redirect',

        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Payload Too Large',
        414: 'URI Too Long',
        415: 'Unsupported Media Type',
        416: 'Range Not Satisfiable',
        417: 'Expectation Failed',
        418: 'I\'m a teapot',
        421: 'Misdirected Request',
        422: 'Unprocessable Entity',
        423: 'Locked',
        424: 'Failed Dependency',
        425: 'Too Early',
        426: 'Upgrade Required',
        428: 'Precondition Required',
        429: 'Too Many Requests',
        431: 'Request Header Fields Too Large',
        451: 'Unavailable For Legal Reasons',

        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
        506: 'Variant Also Negotiates',
        507: 'Insufficient Storage',
        508: 'Loop Detected',
        510: 'Not Extended',
        511: 'Network Authentication Required',
        513: 'The Server Is In A Bad Mood'
    }

    # The response code this instance represents
    __responseCode = 200


    def __init__(self, respCode: int):
        if respCode not in self.__numToTxt:
            raise NotAllowedHttpResponseCode(respCode)

        self.__responseCode = respCode


    def asText(self) -> str:
        """
            Returns the string representation of the response code
        :return:
        """
        return '{responseCode} {responseText}'.format(
                responseCode=self.__responseCode,
                responseText=self.__numToTxt[self.__responseCode]
            )


    def __str__(self) -> str:
        return self.asText()




class Response(object):
    """
        Response, that is sent back to the web server
    """
    __request = None
    __startResponse = None

    contentType = 'text/plain'
    charset     = 'utf-8'
    returnCode  = 200

    __arrHeaders = {}
    __arrCookies = {}

    # The content to send as a byte array
    __byteContent = None

    # The content to send as a string
    __stringContent = ''


    def __init__(self, request: Request, startResponse):
        self.__request       = request
        self.__startResponse = startResponse

    # Getters for the private properties
    @property
    def request(self) -> Request:
        return self.__request

    @property
    def stringContent(self):
        return self.__stringContent

    @stringContent.setter
    def stringContent(self, strCont: str):
        self.__byteContent   = None
        self.__stringContent = strCont

    def addHeader(self, key: str, value: str):
        """
            Adds a header line to the response.
            An already added header is overwritten
        """
        self.__arrHeaders[key] = value
        return self

    def addCookie(self, cookie: Cookie):
        """
            Adds a cookie to the response.
            A already added cookie is overwritten
        """
        self.__arrCookies[cookie.key] = cookie
        return self

    def getContent(self) -> list[bytes]:
        """
            Returns the rendered content.
            startResponse has been called before.
        :return:
        """
        # Run startResponse to the web server
        self.__startResponse(
            ResponseCodeToText(respCode=self.returnCode).asText(),
            self.__buildHeader()
        )

        if self.__byteContent is None:
            # Byte content has not been created yet
            self.__byteContent = bytes(self.__stringContent, self.charset)

        # Return the byte content
        return [self.__byteContent]


    def __buildHeader(self) -> list[tuple]:
        arrHeader = [
            ('Content-type', '{contType}; charset={charSet}'.format(contType=self.contentType, charSet=self.charset)),
            ('Access-Control-Allow-Origin', '*')
        ]

        for key in self.__arrHeaders:
            arrHeader.append((key, self.__arrHeaders[key]))

        for key in self.__arrCookies:
            arrHeader.append(('Set-Cookie', str(self.__arrCookies[key])))

        return arrHeader

