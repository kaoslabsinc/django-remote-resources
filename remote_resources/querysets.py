from itertools import islice

from building_blocks.models.querysets import BulkUpdateCreateQuerySet
from django.db import models, transaction


class RemoteResourceQuerySet(BulkUpdateCreateQuerySet, models.QuerySet):
    def _bulk_update_or_create_helper(self, obj_list):
        model = self.model
        key_field = model.remote_to_model_fields_map[model.remote_data_key_field]
        return self.bulk_update_or_create(obj_list, key_field, [
            model.remote_to_model_fields_map[field]
            for field in model.remote_to_model_fields_map.keys()
            if field != model.remote_data_key_field
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
