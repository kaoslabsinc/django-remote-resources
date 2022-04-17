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

    @staticmethod
    def _get_remote_data_iterator(get_remote_data, start_page=1, max_pages=None, *args, **kwargs):
        page = start_page
        while data := get_remote_data(page=page, *args, **kwargs):
            yield data
            page += 1
            if max_pages and page >= start_page + max_pages:
                break

    def _download(self, remote_data_iterator, *args, **kwargs):
        qs = self.none()
        for data_list in remote_data_iterator(*args, **kwargs):
            with transaction.atomic():
                qs |= self._bulk_update_or_create_helper([
                    self.model.from_remote_data(item)
                    for item in data_list
                ])
        return qs

    def _get_remote_data_list(self, *args, **kwargs):
        raise NotImplementedError

    def download(self, max_pages=None, *args, **kwargs):
        def remote_data_iterator(*args, **kwargs):
            return self._get_remote_data_iterator(self._get_remote_data_list, max_pages=max_pages, *args, **kwargs)

        return self._download(remote_data_iterator, *args, **kwargs)
