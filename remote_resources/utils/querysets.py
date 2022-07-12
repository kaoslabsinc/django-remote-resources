from django.core.paginator import Paginator
from django.db import models


class PageableQuerySet(models.QuerySet):
    """

    """

    def paginate(self, limit, simple=True, mutating=False):
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
                page.object_list
                for page in Paginator(pk_values, limit)
            )
            while paginated_pks:
                pks_page = paginated_pks[0]
                yield qs.filter(pk__in=pks_page)
                paginated_pks = paginated_pks[1:]
