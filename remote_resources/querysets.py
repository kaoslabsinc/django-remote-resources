from building_blocks.models.querysets import BulkUpdateCreateQuerySet
from django.db import models, transaction

from .enums import Ordering
from .utils.itertools import limit_iterator


class RemoteResourceQuerySet(BulkUpdateCreateQuerySet, models.QuerySet):
    client_cls = None  # ACMEClient
    list_api_iterator = None  # ACMEClient.list_users

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
        return self.list_api_iterator(self.client_cls(), *args, **kwargs)

    def _download(self, iterator):
        for data_list in iterator:
            with transaction.atomic():
                yield self._bulk_update_or_create_helper([
                    self.model.from_remote_data(item)
                    for item in data_list
                ])

    def download(self, max_pages=None, *args, **kwargs):
        iterator = limit_iterator(self.get_remote_data_iterator(*args, **kwargs), max_pages)
        return self._download(iterator)


class TimeSeriesQuerySetMixin(models.QuerySet):
    get_latest_by_field = None

    def _get_get_latest_by_field(self):
        return self.get_latest_by_field or self.model._meta.get_latest_by

    def _get_dt_helper(self, qs_method):
        get_latest_by_field = self._get_get_latest_by_field()
        try:
            obj = qs_method(self, get_latest_by_field)
            return getattr(obj, get_latest_by_field)
        except self.model.DoesNotExist:
            return None

    def _get_earliest_dt(self):
        return self._get_dt_helper(self.earliest)

    def _get_latest_dt(self):
        return self._get_dt_helper(self.latest)


class AscTimeSeriesRemoteResource(TimeSeriesQuerySetMixin, RemoteResourceQuerySet):
    def get_remote_data_iterator(self, refresh=False, *args, **kwargs):
        if refresh:
            start_dt, end_dt = None, None
        else:
            start_dt, end_dt = self._get_latest_dt(), None

        return super(AscTimeSeriesRemoteResource, self).get_remote_data_iterator(
            ordering=Ordering.earlier_first,
            start_dt=start_dt,
            end_dt=end_dt,
            *args, **kwargs,
        )


class DescTimeSeriesRemoteResource(TimeSeriesQuerySetMixin, RemoteResourceQuerySet):
    def get_remote_data_iterator(self, fill=False, refresh=False, *args, **kwargs):
        if refresh:
            start_dt, end_dt = None, None
        elif fill:
            start_dt, end_dt = None, self._get_earliest_dt()
        else:
            start_dt, end_dt = self._get_latest_dt(), None

        return super(DescTimeSeriesRemoteResource, self).get_remote_data_iterator(
            ordering=Ordering.later_first,
            start_dt=start_dt,
            end_dt=end_dt,
            *args, **kwargs,
        )
