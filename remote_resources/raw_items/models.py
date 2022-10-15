from typing import Any

from django.db import models

from .querysets import RawItemQuerySet


class AbstractRawItem(models.Model):
    class Meta:
        abstract = True

    source: Any
    processed_item: models.Model | None

    objects = RawItemQuerySet.as_manager()

    def process(self, *args, **kwargs):
        raise NotImplementedError
