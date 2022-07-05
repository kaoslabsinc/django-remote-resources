from django.db import models
from django.db.models import F


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
