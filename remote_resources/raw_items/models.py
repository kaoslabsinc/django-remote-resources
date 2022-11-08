from typing import Any

from django.db import models
from model_utils.models import TimeStampedModel

from .querysets import RawItemQuerySet


class AbstractRawItem(
    TimeStampedModel,
    models.Model
):
    class Meta:
        abstract = True

    raw: Any
    source: Any
    processed_item: models.Model | None

    objects = RawItemQuerySet.as_manager()

    def process(self, *args, **kwargs):
        raise NotImplementedError
