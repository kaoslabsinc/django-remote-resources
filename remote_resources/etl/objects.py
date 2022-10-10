from copy import deepcopy
from typing import Generator, Sequence

from .clients import RemoteClient
from .consts import ALL, MISSING
from .fields import RemoteField


class BaseRemoteObjectMeta(type):
    def __new__(mcs, classname, bases, classdict, **kwds):
        cls = super().__new__(mcs, classname, bases, classdict, **kwds)

        cls.fields = {}
        for attr, val in vars(cls).items():
            if isinstance(val, RemoteField):
                field = val
                field.name = attr
                cls.fields[field.name] = field

        cls._remote_client = None

        return cls

    @property
    def remote_client(cls) -> RemoteClient:
        if cls._remote_client is None:
            cls._remote_client = cls.remote_client_cls()
        return cls._remote_client

    @remote_client.setter
    def remote_client(cls, new_remote_client: RemoteClient):
        cls._remote_client = new_remote_client


class BaseRemoteObject(metaclass=BaseRemoteObjectMeta):
    remote_client_cls: RemoteClient = RemoteClient

    class DoesNotExist(Exception):
        pass

    class MultipleObjectsReturned(Exception):
        pass

    def __init__(self):
        self._json = None
        self.fields = deepcopy(self.fields)

    @property
    def is_loaded(self):
        return self._json is not None

    @property
    def remote_id(self):
        raise NotImplementedError

    @property
    def is_local_only(self):
        return self.remote_id is None

    @property
    def is_edited(self):
        if self.is_local_only:
            return True
        for field_name, field in self.fields.items():
            if field.value is MISSING:
                pass
            elif field.value != getattr(self, field_name):
                return True
        return False

    @classmethod
    def from_json(cls, json):
        instance = cls()
        instance._load_json(json)
        return instance

    def _load_json(self, json) -> None:
        self._json = json
        for field_name, field in self.fields.items():
            cleaned_val = field.etl(json)
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
    def from_obj(cls, obj):
        return cls.from_kwargs(**cls._obj_to_kwargs(obj))

    @classmethod
    def _obj_to_kwargs(cls, obj):
        return {attr: val for attr, val in vars(obj).items() if attr in cls.fields}


class ListRemoteObjectMixin:
    @classmethod
    def _remote_list_all(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def list_all(cls, *args, **kwargs) -> Generator['RemoteObject', None, None]:
        yield from map(cls.from_json, cls._remote_list_all(*args, **kwargs))

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


class RetrieveRemoteObjectMixin:
    @classmethod
    def retrieve(cls, *args, **kwargs):
        return cls.from_json(cls.remote_client.retrieve(*args, **kwargs))

    def refresh(self):
        json = self.remote_client.retrieve(self.remote_id)
        self._load_json(json)


class CreateRemoteObjectMixin:
    def _create(self):
        args, kwargs = self._get_create_args()
        json = self.remote_client.create(*args, **kwargs)
        self._load_json(json)

    def duplicate(self):
        assert not self.is_local_only
        self._create()

    def create(self):
        assert self.is_local_only
        self._create()

    def _get_create_args(self) -> tuple[Sequence, dict]:
        raise NotImplementedError


class UpdateRemoteObjectMixin:
    def update(self, fields: Sequence | type(ALL) = ALL):
        assert not self.is_local_only and self.is_edited
        args, kwargs = self._get_update_args(fields)
        json = self.remote_client.update(self.remote_id, *args, **kwargs)
        self._load_json(json)

    def _get_update_args(self, fields: Sequence | type(ALL)) -> tuple[Sequence, dict]:
        raise NotImplementedError


class DeleteRemoteObjectMixin(BaseRemoteObject):
    def delete(self):
        return self.remote_client.delete(self.remote_id)


class ListCreateRemoteObjectMixin(ListRemoteObjectMixin, CreateRemoteObjectMixin):
    @classmethod
    def get_or_create(cls, defaults=None, **kwargs):
        """"""
        try:
            instance = cls.get(**kwargs)
        except cls.MultipleObjectsReturned:
            raise
        except cls.DoesNotExist:
            instance: GetOrCreateRemoteObject = cls.from_kwargs(**kwargs, **defaults)
            instance.create()
        return instance

    @classmethod
    def update_or_create(cls, defaults=None, **kwargs):
        """"""
        try:
            instance: UpdateRemoteObject = cls.get(**kwargs)
        except cls.MultipleObjectsReturned:
            raise
        except cls.DoesNotExist:
            instance = cls.from_kwargs(**kwargs, **defaults)
            instance.create()
        else:
            instance.update_from_kwargs(**defaults)
            instance.update(fields=defaults.keys())
        return instance


class RemoteObject(
    ListCreateRemoteObjectMixin,
    RetrieveRemoteObjectMixin,
    UpdateRemoteObjectMixin,
    DeleteRemoteObjectMixin,
    BaseRemoteObject
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
    'RemoteObject',
)
