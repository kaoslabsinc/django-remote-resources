from django.core.management.base import BaseCommand


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

    def download(self, options):
        return self.get_queryset().download(**self._pick_options(options))

    def post_process_page(self, qs):
        return None

    def post_process_all(self, accum_qs):
        return None

    def add_arguments(self, parser):
        parser.add_argument('--maxpages', type=int, dest='max_pages')

    def handle(self, *args, **options):
        total_count = 0
        accum_qs = self.get_queryset().none()

        for page, qs in enumerate(self.download(options)):
            self._write_success_page_downloaded(qs, page)
            total_count += qs.count()
            if self.accumulate_qs:
                accum_qs |= qs
            post_process_qs = self.post_process_page(qs)
            self._write_success_page_post_processed(post_process_qs, page)

        self.post_process_all(accum_qs)
        self._write_success_done(total_count=total_count)


__all__ = [
    'DownloadResourceCommand'
]
