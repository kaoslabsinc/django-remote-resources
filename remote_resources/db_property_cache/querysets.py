from abc import ABC
from typing import Tuple, Any

from django.db import models
from django.db.models import F


class HasCachedPropertiesQuerySet(ABC, models.QuerySet):
    """
    Represents a QuerySet for an object that has cached properties.
    Generally used alongside models who inherit from HasCachedProperties

    You'd want to override and define method _refresh_annotations

    ...

    Attributes
    ----------
    cached_properties : list
        a list of properties that are cached

    Methods
    -------
    ready(fresh=False)
        Annotate all property fields. Load the values from cache or freshly calculate them.

    refresh()
        Flush the cache, refresh the annotations and then update the cache with the new values
    """

    cached_properties = []

    def _flush_cache(self):
        return self.update(**{
            f'_cached_{field}': None
            for field in self.cached_properties
        })

    def update_cache(self, *args):
        return self.update(**{
            f'_cached_{field}': F(field)
            for field in (args or self.cached_properties)
        })

    def _load_cache(self):
        return self.annotate(**{
            field: F(f'_cached_{field}')
            for field in self.cached_properties
        })

    def _refresh_annotations(self) -> 'HasCachedPropertiesQuerySet':
        """
        Override this method for the logic that loads up the values for the properties as queryset annotations.

        Returns
        -------
        HasCachedPropertiesQuerySet
            a queryset with all property fields annotated from fresh values
        """
        raise NotImplementedError

    def ready(self, fresh=False) -> 'HasCachedPropertiesQuerySet':
        """
        Annotates all property fields. Loads the values from cache if fresh is false or freshly calculates them if true.

        Parameters
        ----------
        fresh : bool, optional
            A flag used to determine whether to calculate fresh data (if True) or load from cache (if False, default)

        Returns
        -------
        HasCachedPropertiesQuerySet
            a queryset with all property fields annotated from fresh values or values loaded from the cache
        """
        return self._refresh_annotations() if fresh else self._load_cache()

    def refresh(self, flush_cache=True) -> tuple['HasCachedPropertiesQuerySet', Any]:
        """
        Flush the cache, refresh the annotations and then update the cache with the new values

        Returns
        -------
        HasCachedPropertiesQuerySet
            A queryset with all property fields annotated from fresh values
        """
        if flush_cache:
            self._flush_cache()
        annotated_qs = self._refresh_annotations()
        return annotated_qs, annotated_qs.update_cache()
