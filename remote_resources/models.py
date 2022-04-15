from django.db import models

_KEY_DOES_NOT_EXIST = '# KEY_DOES_NOT_EXIST_xz7r5b'


class AbstractRemoteResource(
    models.Model
):
    class Meta:
        abstract = True

    remote_to_model_fields_map = {}
    remote_data_key_field = None

    _json = models.JSONField()

    @classmethod
    def from_remote_data(cls, item, **kwargs):
        return cls(
            _json=item,
            **{
                model_field: item[remote_field]
                for remote_field, model_field in cls.remote_to_model_fields_map.items()
                if remote_field in item
            },
            **kwargs
        )
