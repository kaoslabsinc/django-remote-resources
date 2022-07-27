import json

from django.db import models

from .querysets import RemoteResourceQuerySet


def _sanitize_json_for_db(item):
    return json.loads(json.dumps(item).replace('\\u0000', ''))


class RemoteResource(
    models.Model
):
    class Meta:
        abstract = True

    remote_to_model_fields_map = {}
    remote_data_key_field = None

    _json = models.JSONField()

    objects = RemoteResourceQuerySet.as_manager()

    @classmethod
    def from_remote_data(cls, item, **kwargs):
        fields_dict = {
            model_field: item[remote_field]
            for remote_field, model_field in cls.remote_to_model_fields_map.items()
            if remote_field in item
        }
        fields_dict.update(kwargs)
        return cls(
            _json=_sanitize_json_for_db(item),
            **fields_dict,
        )
