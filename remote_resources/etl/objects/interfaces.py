from abc import ABC, abstractmethod
from typing import Type, Any

from py_kaos_utils.typing import T

from ..clients import RemoteClient
from ..fields import RemoteField


class InitFromJsonInterface(ABC):
    _json: Any

    @classmethod
    def from_json(cls, json):
        instance = cls()
        instance._load_json(json)
        return instance

    @abstractmethod
    def _load_json(self, json) -> None:
        self._json = json

    @property
    def is_loaded(self):
        return self._json is not None


class InitFromKwargsInterface(ABC):
    @classmethod
    @abstractmethod
    def from_kwargs(cls: Type[T], **kwargs) -> T:
        pass


class InitFromObjInterface(InitFromKwargsInterface, ABC):
    @classmethod
    def from_obj(cls: Type[T], obj) -> T:
        return cls.from_kwargs(**cls._obj_to_kwargs(obj))

    @classmethod
    def _obj_to_kwargs(cls, obj) -> dict[str, Any]:
        return {attr: val for attr, val in vars(obj).items()}


class UpdateFromKwargsInterface(ABC):
    def _update_from_kwargs(self, **kwargs) -> None:
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)


class RemoteObjectInterface(
    InitFromJsonInterface,
    InitFromObjInterface,
):
    remote_client: RemoteClient
    fields: dict[str, RemoteField]

    @property
    @abstractmethod
    def remote_id(self):
        raise NotImplementedError

    @property
    def is_local_only(self):
        return self.remote_id is None

    @property
    @abstractmethod
    def is_edited(self):
        if self.is_local_only:
            return True


__all__ = (
    'InitFromJsonInterface',
    'InitFromKwargsInterface',
    'InitFromObjInterface',
    'UpdateFromKwargsInterface',
    'RemoteObjectInterface',
)
