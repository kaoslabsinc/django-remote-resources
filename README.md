# Django remote resources

Sync remote API resources to Django models

## Quick start

    pip install django-remote-resources

Add `AbstractRemoteResource` to your model (1), and define a mapping between the fields in the remote data to your
model's fields (2), and create a custom QuerySet manager for the model, inheriting from `RemoteResourceQuerySet` and
define method `get_remote_data_iterator` (3). Optionally define a `remote_data_key_field` that points to a unique
identifier on the remote data (4).

```python
class ResourceMirrorQuerySet(  # (3)
    RemoteResourceQuerySet
):
    def get_remote_data_iterator(self, *args, **kwargs):
        client = RemoteClient()
        return client.get_data(**kwargs)  # should return an iterator, with each item representing a page of data


class ResourceMirror(
    AbstractRemoteResource,  # (1)
    models.Model
):
    remote_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField()

    objects = ResourceMirrorQuerySet.as_manager()  # (3)

    remote_to_model_fields_map = {  # (2)
        'id': 'remote_id',
        'name': 'name',
        'email': 'email',
    }
    remote_data_key_field = 'id'  # (4)
```

## Development and Testing

### IDE Setup

Add the `example` directory to the `PYTHONPATH` in your IDE to avoid seeing import warnings in the `tests` modules. If
you are using PyCharm, this is already set up.

### Running the Tests

Install requirements

```
pip install -r requirements.txt
```

For local environment

```
pytest
```

For all supported environments

```
tox
```
