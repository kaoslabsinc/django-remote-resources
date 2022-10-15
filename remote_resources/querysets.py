import logging

from django.db import models
from py_kaos_utils.pagination import paginate_generator

from remote_resources.consts import SAVE_AND_CONTINUE, SAVE_AND_BREAK, BREAK

logger = logging.getLogger()


class RemoteObjectModelQuerySet(models.QuerySet):
    def _download_check(self, page):
        return SAVE_AND_CONTINUE

    def download(self, *args, **kwargs):
        model = self.model
        generator = model.remote_obj_cls.list_all(*args, **kwargs)

        all_objs = []
        for i, page in enumerate(paginate_generator(generator, model.remote_paginated_by)):
            check = self._download_check(page)
            if check in {SAVE_AND_CONTINUE, SAVE_AND_BREAK}:
                objs = self.bulk_create(model.from_remote_obj(obj) for obj in page)
                logger.info(f"({i + 1}) Saved {len(objs)} {model._meta.verbose_name_plural}")
                all_objs.extend(objs)
            if check in {BREAK, SAVE_AND_BREAK}:
                break

        return all_objs


__all__ = (
    'RemoteObjectModelQuerySet',
)
