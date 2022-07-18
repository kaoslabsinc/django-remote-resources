class RefreshableCommandMixin:
    download_options = (
        'refresh',
    )

    def add_arguments(self, parser):
        super(RefreshableCommandMixin, self).add_arguments(parser)
        parser.add_argument('--refresh', action='store_true')


class FillableCommandMixin:
    download_options = (
        'fill',
    )

    def add_arguments(self, parser):
        super(FillableCommandMixin, self).add_arguments(parser)
        parser.add_argument('--fill', action='store_true')


__all__ = [
    'RefreshableCommandMixin',
    'FillableCommandMixin',
]
