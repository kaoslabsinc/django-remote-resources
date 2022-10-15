from django.db import models


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
