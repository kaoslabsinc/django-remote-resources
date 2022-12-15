from django.db import models, transaction
from django.db.models import Case, Value, When
from py_kaos_utils.logging import ProgressLogger


class RawItemQuerySet(models.QuerySet):
    process_batch_size = 0

    def _bulk_update_processed_item(self, processed_raw_items):
        return self.bulk_update(processed_raw_items, ('processed_item',))

    def process(self, *args, **kwargs):
        plogger = ProgressLogger(self.count(), 100)

        count_updated = 0
        processed_raw_items = []

        def commit_batch():
            with transaction.atomic():
                count = self._bulk_update_processed_item(processed_raw_items)
            plogger.log_progress(count)
            return count

        for obj in self.all().order_by('created'):
            processed_item = obj.process(*args, **kwargs)
            obj.processed_item = processed_item
            processed_raw_items.append(obj)

            if len(processed_raw_items) == self.process_batch_size:
                commit_batch()
                processed_raw_items = []

        if processed_raw_items:
            commit_batch()

        return count_updated

    def annotate_is_processed(self):
        return self.annotate(is_processed=Case(
            When(processed_item__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField()
        ))
