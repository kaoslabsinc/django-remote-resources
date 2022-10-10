from abc import ABCMeta, abstractmethod, ABC
from copy import deepcopy
from typing import Generator, Sequence, Type

from .interfaces import RemoteObjectInterface, UpdateFromKwargsInterface
from ..clients import RemoteClient
from ..consts import ALL, MISSING
from ..fields import RemoteField


class BaseRemoteObjectMeta(ABCMeta):
    remote_client_cls: Type[RemoteClient]

    def __init__(cls, name, bases, dct):
        super(BaseRemoteObjectMeta, cls).__init__(name, bases, dct)

        cls.fields = {}
        for attr, val in vars(cls).items():
            if isinstance(val, RemoteField):
                field = val
                field.name = attr
                cls.fields[field.name] = field

        cls._remote_client = None

    @property
    def remote_client(cls) -> RemoteClient:
        if cls._remote_client is None:
            cls._remote_client = cls.remote_client_cls()
        return cls._remote_client

    @remote_client.setter
    def remote_client(cls, new_remote_client: RemoteClient):
        cls._remote_client = new_remote_client


class BaseRemoteObject(
    RemoteObjectInterface, ABC,
    metaclass=BaseRemoteObjectMeta
):
    def __init__(self):
        self._raw = None
        self.fields = deepcopy(self.fields)

    @property
    def is_edited(self):
        if super(BaseRemoteObject, self).is_edited:
            return True
        for field_name, field in self.fields.items():
            if field.value is MISSING:
                pass
            elif field.value != getattr(self, field_name):
                return True
        return False

    def _load_raw(self, raw) -> None:
        super(BaseRemoteObject, self)._load_raw(raw)
        for field_name, field in self.fields.items():
            cleaned_val = field.etl(raw)
            setattr(self, field_name, cleaned_val)

    @classmethod
    def from_kwargs(cls, **kwargs):
        instance = cls()
        for field_name, field in instance.fields.items():
            val = kwargs.get(field_name, MISSING)
            if val is MISSING and not field.required:
                val = field.default
            setattr(instance, field_name, val)
            field.value = val
        return instance

    @classmethod
    def _obj_to_kwargs(cls, obj):
        kwargs = super(BaseRemoteObject, cls)._obj_to_kwargs(obj)
        return {attr: val for attr, val in kwargs if attr in cls.fields}


class ListRemoteObjectMixin(
    RemoteObjectInterface, ABC
):
    class DoesNotExist(Exception):
        pass

    class MultipleObjectsReturned(Exception):
        pass

    @classmethod
    @abstractmethod
    def _remote_list_all(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def list_all(cls, *args, **kwargs) -> Generator['ListRemoteObjectMixin', None, None]:
        yield from map(cls.from_raw, cls._remote_list_all(*args, **kwargs))

    @classmethod
    def get(cls, *args, **kwargs):
        list_all_generator = cls.list_all(*args, **kwargs)
        try:
            obj = next(list_all_generator)
        except StopIteration:
            raise cls.DoesNotExist("Object matching query does not exist")
        else:
            try:
                next(list_all_generator)
            except StopIteration:
                return obj
            else:
                raise cls.MultipleObjectsReturned("get() returned more than one objects")


class RetrieveRemoteObjectMixin(
    RemoteObjectInterface, ABC
):
    @classmethod
    def retrieve(cls, *args, **kwargs):
        return cls.from_raw(cls.remote_client.retrieve(*args, **kwargs))

    def refresh(self):
        json = self.remote_client.retrieve(self.remote_id)
        self._load_raw(json)


class CreateRemoteObjectMixin(
    RemoteObjectInterface, ABC
):
    def _create(self):
        args, kwargs = self._get_create_args()
        json = self.remote_client.create(*args, **kwargs)
        self._load_raw(json)

    def duplicate(self):
        assert not self.is_local_only
        self._create()

    def create(self):
        assert self.is_local_only
        self._create()

    @abstractmethod
    def _get_create_args(self) -> tuple[Sequence, dict]:
        raise NotImplementedError


class UpdateRemoteObjectMixin(
    UpdateFromKwargsInterface,
    RemoteObjectInterface, ABC
):
    def update(self, fields: Sequence | type(ALL) = ALL):
        assert not self.is_local_only and self.is_edited
        args, kwargs = self._get_update_args(fields)
        json = self.remote_client.update(self.remote_id, *args, **kwargs)
        self._load_raw(json)

    @abstractmethod
    def _get_update_args(self, fields: Sequence | type(ALL)) -> tuple[Sequence, dict]:
        raise NotImplementedError

    def _update_from_kwargs(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.fields:
                setattr(self, key, val)


class DeleteRemoteObjectMixin(
    RemoteObjectInterface, ABC
):
    def delete(self):
        return self.remote_client.delete(self.remote_id)


class ListCreateRemoteObjectMixin(
    ListRemoteObjectMixin,
    CreateRemoteObjectMixin, ABC
):
    @classmethod
    def get_or_create(cls, defaults=None, **kwargs):
        """"""
        try:
            instance = cls.get(**kwargs)
        except cls.MultipleObjectsReturned:
            raise
        except cls.DoesNotExist:
            instance: ListCreateRemoteObjectMixin = cls.from_kwargs(**kwargs, **defaults)
            instance.create()
        return instance


class ListCreateUpdateRemoteObjectMixin(
    ListRemoteObjectMixin,
    CreateRemoteObjectMixin,
    UpdateRemoteObjectMixin, ABC
):
    @classmethod
    def update_or_create(cls, defaults=None, **kwargs):
        """"""
        try:
            instance = cls.get(**kwargs)
        except cls.MultipleObjectsReturned:
            raise
        except cls.DoesNotExist:
            instance = cls.from_kwargs(**kwargs, **defaults)
            instance.create()
        else:
            instance._update_from_kwargs(**defaults)
            instance.update(fields=defaults.keys())
        return instance


class RemoteObject(
    ListCreateUpdateRemoteObjectMixin,
    RetrieveRemoteObjectMixin,
    DeleteRemoteObjectMixin,
    BaseRemoteObject, ABC
):
    """"""


__all__ = (
    'BaseRemoteObject',
    'ListRemoteObjectMixin',
    'CreateRemoteObjectMixin',
    'RetrieveRemoteObjectMixin',
    'UpdateRemoteObjectMixin',
    'DeleteRemoteObjectMixin',
    'ListCreateRemoteObjectMixin',
    'ListCreateUpdateRemoteObjectMixin',
    'RemoteObject',
)
