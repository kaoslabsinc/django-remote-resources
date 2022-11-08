from building_blocks.models import Archivable, SluggedKaosModel, KaosModel, OrderableModel
from django.db import models


class Form(
    SluggedKaosModel
):
    pass


class FormFieldType(models.TextChoices):
    single_choice = 'single_choice'
    multi_choice = 'multi_choice'
    long_text = 'long_text'


class FormField(
    OrderableModel,
    KaosModel
):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='fields')
    slug = models.SlugField(max_length=255)
    type = models.CharField(max_length=30, choices=FormFieldType.choices)

    choices = models.JSONField(default=list, blank=True)
    choices_endpoint = models.CharField(max_length=255, blank=True)

    class Meta(OrderableModel.Meta):
        unique_together = ('form', 'slug')
        ordering = ('form', *OrderableModel.Meta.ordering)

    def __str__(self):
        return f"{self.name} field on {self.form}"


class ClipperEndpoint(
    Archivable,
    SluggedKaosModel
):
    post_endpoint = models.CharField(max_length=255)
    form = models.ForeignKey(Form, on_delete=models.SET_NULL, null=True, blank=True)


__all__ = (
    'Form',
    'FormField',
    'FormFieldType',
    'ClipperEndpoint'
)
