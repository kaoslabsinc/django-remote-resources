from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models import Case, Value, When


class RawItemQuerySet(models.QuerySet):
    process_batch_size = 0

    def process(self, *args, **kwargs):
        processed_raw_items = []
        count_updated = 0

        if isinstance(self.model.processed_item, GenericForeignKey):
            bulk_update_fields = ('_pi_content_type', '_pi_object_id')
        else:
            bulk_update_fields = ('processed_item',)

        for obj in self.all():
            processed_item = obj.process(*args, **kwargs)
            obj.processed_item = processed_item
            processed_raw_items.append(obj)

            if len(processed_raw_items) == self.process_batch_size:
                count_updated += self.bulk_update(processed_raw_items, bulk_update_fields)
                processed_raw_items = []

        if processed_raw_items:
            count_updated += self.bulk_update(processed_raw_items, bulk_update_fields)

        return count_updated

    def annotate_is_processed(self):
        return self.annotate(is_processed=Case(
            When(processed_item__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField()
        ))
