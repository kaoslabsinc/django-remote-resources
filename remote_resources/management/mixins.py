class RefreshableCommandMixin:
    download_options = (
        'refresh',
    )

    def add_arguments(self, parser):
        super(RefreshableCommandMixin, self).add_arguments(parser)
        parser.add_argument('--refresh', action='store_true')


__all__ = [
    'RefreshableCommandMixin'
]
