from django.core.paginator import Paginator
from django.db import models
from django.db.models import Min, Max


class PageableQuerySet(models.QuerySet):
    """

    """

    def paginate(self, limit):
        d = self.aggregate(min=Min('id'), max=Max('id'))
        min_id, max_id = d['min'], d['max']
        if min_id is None:
            return self
        for i in range(min_id, max_id + 1, limit):
            yield self.filter(id__gte=i, id__lt=i + limit)

    def paginate_dprc(self, limit, simple=True, mutating=False):
        """

        :param limit:
        :param simple:
        :param mutating:
        :return:
        """

        qs = self.model.objects.all() if simple else self
        pk_values = self.values_list('pk', flat=True)

        if not mutating:
            for page in Paginator(pk_values, limit):
                yield qs.filter(pk__in=page.object_list)
        else:
            paginated_pks = tuple(
                tuple(page.object_list)
                for page in Paginator(pk_values, limit)
            )
            while paginated_pks:
                pks_page = paginated_pks[0]
                yield qs.filter(pk__in=pks_page)
                paginated_pks = paginated_pks[1:]
