
class Base(Exception):
    pass


class ProtocolException(Base):
    pass


class ParamNotFound(Base):
    pass


class ValueNotFound(Base):
    pass


class NotAllowedHttpMethod(Base):
    pass


class NotAllowedHttpResponseCode(Base):
    pass


class InvalidData(Base):
    pass


class NotUnique(Base):
    pass
