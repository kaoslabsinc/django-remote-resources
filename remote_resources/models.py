from typing import Callable, Any

from django.db import models

from remote_resources.etl import RemoteObject
from .querysets import RemoteObjectModelQuerySet

ExtractType = Callable[[RemoteObject], Any]


class RemoteObjectModel(
    models.Model
):
    class Meta:
        abstract = True

    remote_obj_cls = None
    remote_paginated_by = 0
    remote_to_model_map: dict[str, str | None | ExtractType | tuple[str, ExtractType]] = {}

    objects = RemoteObjectModelQuerySet.as_manager()

    @classmethod
    def from_remote_obj(cls, obj: RemoteObject):
        create_kwargs = {}
        for remote_attr in obj.fields_and_properties:
            conf = cls.remote_to_model_map.get(remote_attr, remote_attr)
            if conf is not None:
                if callable(conf):
                    func = conf
                    model_field = remote_attr
                elif isinstance(conf, tuple):
                    model_field, func = conf
                else:
                    model_field = conf
                    func = lambda obj: getattr(obj, remote_attr)
                create_kwargs[model_field] = func(obj)
        return cls(**create_kwargs)


__all__ = (
    'RemoteObjectModel',
)
