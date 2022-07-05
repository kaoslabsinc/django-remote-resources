from django.db import models
from django.db.models import Min, Max


class PageableQuerySet(models.QuerySet):
    def paginate(self, limit):
        min_id = self.aggregate(m=Min('id'))['m']
        if min_id is None:
            return self
        max_id = self.aggregate(m=Max('id'))['m']
        for i in range(min_id, max_id + 1, limit):
            yield self.filter(id__gte=i, id__lt=i + limit)
