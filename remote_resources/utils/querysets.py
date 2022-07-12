from django.core.paginator import Paginator
from django.db import models


class PageableQuerySet(models.QuerySet):
    """

    """

    def paginate(self, limit, simple=True):
        """

        :param limit:
        :param simple:
        :return:
        """

        paginated_pks = tuple(
            page.object_list
            for page in Paginator(
                self.values_list('pk', flat=True),
                limit
            )
        )

        qs = self.model.objects.all() if simple else self

        while paginated_pks:
            pks_page = paginated_pks[0]
            yield qs.filter(pk__in=pks_page)
            paginated_pks = paginated_pks[1:]
