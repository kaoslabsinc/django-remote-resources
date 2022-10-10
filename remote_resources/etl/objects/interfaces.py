from abc import ABC, abstractmethod
from typing import Any, Type

from ..clients import RemoteClient
from ..fields import RemoteField


class InitFromRawInterface(ABC):
    _raw: Any

    def __init__(self):
        self._raw = None

    @classmethod
    def from_raw(cls, raw_obj):
        instance = cls()
        instance._load_raw(raw_obj)
        return instance

    @abstractmethod
    def _load_raw(self, raw) -> None:
        self._raw = raw

    @property
    def is_loaded(self):
        return self._raw is not None


class InitFromKwargsInterface(ABC):
    @classmethod
    @abstractmethod
    def from_kwargs(cls, **kwargs):
        pass


class InitFromObjInterface(InitFromKwargsInterface, ABC):
    @classmethod
    def from_obj(cls, obj):
        return cls.from_kwargs(**cls._obj_to_kwargs(obj))

    @classmethod
    def _obj_to_kwargs(cls, obj) -> dict[str, Any]:
        return {attr: val for attr, val in vars(obj).items()}


class UpdateFromKwargsInterface(ABC):
    def _update_from_kwargs(self, **kwargs) -> None:
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)


class HasRemoteClientInterface:
    remote_client_cls: Type[RemoteClient]
    remote_client: RemoteClient


class HasFieldsInterface:
    fields: dict[str, RemoteField]


__all__ = (
    'InitFromRawInterface',
    'InitFromKwargsInterface',
    'InitFromObjInterface',
    'UpdateFromKwargsInterface',
    'HasRemoteClientInterface',
    'HasFieldsInterface',
)
