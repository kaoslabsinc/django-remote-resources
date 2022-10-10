from .consts import NOT_PROVIDED, MISSING


class RemoteField:
    def __init__(self, label=None, required=False, default=NOT_PROVIDED,
                 extract=None, clean=None):
        self.name = None
        self.value = MISSING

        self.label = label
        self.required = required
        self.default = default

        self._extract = extract
        self._clean = clean

    def extract_raw_value(self, raw_obj):
        """
        Extract the raw value for this field from the object.
        raw_obj: The object at large.
        """
        if self._extract is not None:
            if callable(self._extract):
                return self._extract(raw_obj)
            if isinstance(self._extract, str):
                return raw_obj[self._extract]
        return raw_obj[self.name]

    def clean(self, raw_value):
        if self._clean:
            return self._clean(raw_value)
        return raw_value

    def etl(self, raw_obj):
        self.value = self.clean(self.extract_raw_value(raw_obj))
        return self.value


__all__ = (
    'RemoteField',
)
