from typing import Any

from django.db import models
from model_utils.models import TimeStampedModel

from .querysets import RawItemQuerySet


class RawItemInterface:
    _raw: Any
    source: Any
    processed_item: models.Model | None

    def process(self, *args, **kwargs):
        raise NotImplementedError


class AbstractRawItem(
    RawItemInterface,
    TimeStampedModel,
    models.Model
):
    class Meta:
        abstract = True

    objects = RawItemQuerySet.as_manager()


__all__ = (
    'RawItemInterface',
    'AbstractRawItem',
)
