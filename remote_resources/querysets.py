from itertools import islice

from building_blocks.models.querysets import BulkUpdateCreateQuerySet
from django.db import models, transaction
from django.db.models import F


class RemoteResourceQuerySet(BulkUpdateCreateQuerySet, models.QuerySet):
    def _bulk_update_or_create_helper(self, obj_list):
        model = self.model

        if model.remote_data_key_field is None:
            key_field = 'pk'
        else:
            key_field = model.remote_to_model_fields_map[model.remote_data_key_field]

        return self.bulk_update_or_create(obj_list, key_field, [
            field
            for field in model.remote_to_model_fields_map.values()
            if field != key_field
        ])

    def get_remote_data_iterator(self, *args, **kwargs):
        raise NotImplementedError

    def _download(self, iterator):
        for data_list in iterator:
            with transaction.atomic():
                yield self._bulk_update_or_create_helper([
                    self.model.from_remote_data(item)
                    for item in data_list
                ])

    @staticmethod
    def _limit_iterator(iterator, max_pages):
        if max_pages:
            iterator = islice(iterator, max_pages)
        return iterator

    def download(self, max_pages=None, *args, **kwargs):
        iterator = self._limit_iterator(self.get_remote_data_iterator(*args, **kwargs), max_pages)
        return self._download(iterator)


class HasCachedPropertiesQuerySet(models.QuerySet):
    cached_properties = []

    def _flush_cache(self):
        return self.update(**{
            f'_cached_{field}': None
            for field in self.cached_properties
        })

    def _refresh_annotations(self):
        raise NotImplementedError

    def _update_cache(self):
        return self.update(**{
            f'_cached_{field}': F(field)
            for field in self.cached_properties
        })

    def refresh(self):
        self._flush_cache()
        return self._refresh_annotations()._update_cache()

    def ready(self):
        return self.annotate(**{
            field: F(f'_cached_{field}')
            for field in self.cached_properties
        })
