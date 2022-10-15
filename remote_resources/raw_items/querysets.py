from django.db import models
from django.db.models import Case, Value, When


class RawItemQuerySet(models.QuerySet):
    def process(self, *args, **kwargs):
        objs = []
        processed_items = []
        for obj in self.all():
            processed_item = obj.process(*args, **kwargs)
            obj.processed_item = processed_item
            objs.append(obj)
            processed_items.append(processed_item)

        return self.bulk_update(objs, ('processed_item',))

    def annotate_is_processed(self):
        return self.annotate(is_processed=Case(
            When(processed_item__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField()
        ))
