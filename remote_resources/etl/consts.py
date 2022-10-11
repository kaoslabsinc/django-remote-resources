# TODO: Consider moving these to py_utils

class ALL_TYPE:
    def __repr__(self):
        return "ALL"


class NOT_PROVIDED_TYPE:
    def __repr__(self):
        return "NOT PROVIDED"


class MISSING_TYPE:
    def __repr__(self):
        return "MISSING"


ALL = ALL_TYPE()
NOT_PROVIDED = NOT_PROVIDED_TYPE()
MISSING = MISSING_TYPE()

__all__ = (
    'ALL',
    'NOT_PROVIDED',
    'MISSING',
)
