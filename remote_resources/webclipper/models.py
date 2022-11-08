from django.db import models
from django.utils.functional import cached_property
from model_utils.models import TimeStampedModel
from scrapy import Selector

from remote_resources.raw_items.models import AbstractRawItem


class AbstractWebClip(
    TimeStampedModel,
    models.Model
):
    class Meta:
        abstract = True

    page_url = models.URLField()
    page_title = models.CharField(max_length=255, blank=True)
    html_content = models.TextField(blank=True)

    def __str__(self):
        return self.page_title or self.page_url

    @cached_property
    def _selector(self):
        return Selector(text=self.html_content)


class WebClipRawItem(
    AbstractRawItem,
    AbstractWebClip
):
    class Meta:
        abstract = True

    @property
    def raw(self):
        return self.html_content


__all__ = (
    'AbstractWebClip',
    'WebClipRawItem',
)
