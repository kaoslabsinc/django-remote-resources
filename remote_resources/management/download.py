from django.core.management.base import BaseCommand

from .mixins import RefreshableCommandMixin, FillableCommandMixin


class DownloadResourceCommand(BaseCommand):
    model = None
    queryset = None
    accumulate_qs = False
    download_options = ('max_pages',)

    @property
    def _opts(self):
        return self.model._meta

    @property
    def help(self):
        return f"Download {self._opts.verbose_name_plural} into the database from a remote resource"

    def _write_success(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def _write_success_page_downloaded(self, qs, page):
        count = qs.count()
        self._write_success(f"({page}) Created or updated {count} {self._opts.verbose_name_plural}")

    def _write_success_done(self, *args, **kwargs):
        total_count = kwargs['total_count']
        self._write_success(f"Created or updated {total_count} {self._opts.verbose_name_plural} in total")

    def _write_success_page_post_processed(self, results, page):
        pass

    def get_queryset(self):
        if self.queryset is None:
            return self.model.objects.all()
        return self.queryset

    def _pick_options(self, options):
        return {k: v for k, v in options.items() if k in self.download_options}

    def download(self, **kwargs):
        return self.get_queryset().download(**kwargs)

    def post_process_page(self, qs):
        return qs

    def post_process_all(self, accum_qs):
        return accum_qs

    def add_arguments(self, parser):
        parser.add_argument('--maxpages', type=int, dest='max_pages')

    def handle(self, *args, **options):
        total_count = 0
        accum_qs = self.get_queryset().none()

        for page, qs in enumerate(self.download(**self._pick_options(options))):
            self._write_success_page_downloaded(qs, page)
            total_count += qs.count()
            if self.accumulate_qs:
                accum_qs |= qs
            post_process_qs = self.post_process_page(qs)
            self._write_success_page_post_processed(post_process_qs, page)

        self.post_process_all(accum_qs)
        self._write_success_done(total_count=total_count)


class DownloadTimeSeriesResourceCommand(RefreshableCommandMixin, DownloadResourceCommand):
    download_options = (
        *DownloadResourceCommand.download_options,
        *RefreshableCommandMixin.download_options,
    )


class DownloadAscTimeSeriesResourceCommand(DownloadTimeSeriesResourceCommand):
    pass


class DownloadDescTimeSeriesResourceCommand(
    RefreshableCommandMixin,
    FillableCommandMixin,
    DownloadResourceCommand
):
    download_options = (
        *DownloadResourceCommand.download_options,
        *RefreshableCommandMixin.download_options,
        *FillableCommandMixin.download_options,
    )


__all__ = [
    'DownloadResourceCommand',
    'DownloadTimeSeriesResourceCommand',
    'DownloadAscTimeSeriesResourceCommand',
    'DownloadDescTimeSeriesResourceCommand'
]
