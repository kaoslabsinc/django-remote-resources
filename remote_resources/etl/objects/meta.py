from typing import Type

from ..clients import RemoteClient
from ..fields import RemoteField


class HasRemoteClientMeta(type):
    remote_client_cls: Type[RemoteClient]

    def __init__(cls, name, bases, dct):
        super(HasRemoteClientMeta, cls).__init__(name, bases, dct)
        cls._remote_client = None

    def get_remote_client(cls):
        if cls._remote_client is None:
            cls._remote_client = cls.remote_client_cls()
        return cls._remote_client

    def set_remote_client(cls, new_remote_client: RemoteClient):
        cls._remote_client = new_remote_client

    remote_client = property(get_remote_client, set_remote_client)


class HasRemoteFieldsMeta(type):
    def __init__(cls, name, bases, dct):
        super(HasRemoteFieldsMeta, cls).__init__(name, bases, dct)
        cls.fields = {}
        for attr, val in vars(cls).items():
            if isinstance(val, RemoteField):
                field = val
                field.name = attr
                cls.fields[field.name] = field
