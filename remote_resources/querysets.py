from building_blocks.models.querysets import BulkUpdateCreateQuerySet
from django.db import models, transaction
from django.db.models import Q

from .enums import Ordering
from .utils.itertools import limit_iterator


class RemoteResourceQuerySet(BulkUpdateCreateQuerySet, models.QuerySet):
    """
    Represents a QuerySet for an object that is a remote resource.
    Generally used alongside models who inherit from RemoteResource

    ...

    Methods
    -------
    download(max_pages=None, *args, **kwargs)
        Download and save remote objects to the DB from the API
    """

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

    def _get_list_api_generator(self):
        """
        Example: return APIClient().list_users
        """
        return lambda *args, **kwargs: iter(())

    def _get_list_api_iterator(self, *args, **kwargs):
        list_api_generator = self._get_list_api_generator()
        return list_api_generator(*args, **kwargs)

    def _save_objects_from_iterator(self, iterator):
        for data_list in iterator:
            with transaction.atomic():
                yield self._bulk_update_or_create_helper([
                    self.model.from_remote_data(item)
                    for item in data_list
                ])

    def download(self, max_pages=None, *args, **kwargs):
        iterator = limit_iterator(self._get_list_api_iterator(*args, **kwargs), max_pages)
        return self._save_objects_from_iterator(iterator)


class TimeSeriesQuerySetMixin(models.QuerySet):
    get_latest_by_field = None
    filter_q = None

    def _get_get_latest_by_field(self):
        return self.get_latest_by_field or self.model._meta.get_latest_by

    def _get_useful_timerange_qs(self):
        return self.filter(self.filter_q or Q())

    def _get_earliest_dt(self):
        get_latest_by_field = self._get_get_latest_by_field()
        filtered_qs = self._get_useful_timerange_qs()
        if obj := filtered_qs.order_by(get_latest_by_field).first():
            return getattr(obj, get_latest_by_field)

    def _get_latest_dt(self):
        return self.reverse()._get_earliest_dt()


class AscTimeSeriesRemoteResourceQuerySet(TimeSeriesQuerySetMixin, RemoteResourceQuerySet):
    def _get_list_api_iterator(self, refresh=False, *args, **kwargs):
        if refresh:
            start_dt, end_dt = None, None
        else:
            start_dt, end_dt = self._get_latest_dt(), None

        return super(AscTimeSeriesRemoteResourceQuerySet, self)._get_list_api_iterator(
            ordering=Ordering.earlier_first,
            start_dt=start_dt,
            end_dt=end_dt,
            *args, **kwargs,
        )


class DescTimeSeriesRemoteResourceQuerySet(TimeSeriesQuerySetMixin, RemoteResourceQuerySet):
    def _get_list_api_iterator(self, fill=False, refresh=False, *args, **kwargs):
        if refresh:
            start_dt, end_dt = None, None
        elif fill:
            start_dt, end_dt = None, self._get_earliest_dt()
        else:
            start_dt, end_dt = self._get_latest_dt(), None

        return super(DescTimeSeriesRemoteResourceQuerySet, self)._get_list_api_iterator(
            ordering=Ordering.later_first,
            start_dt=start_dt,
            end_dt=end_dt,
            *args, **kwargs,
        )
