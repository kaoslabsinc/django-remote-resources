class BREAK_TYPE:
    pass


class SAVE_AND_CONTINUE_TYPE:
    pass


class SAVE_AND_BREAK_TYPE:
    pass


class BREAK(BREAK_TYPE):
    pass


class SAVE_AND_CONTINUE(SAVE_AND_CONTINUE_TYPE):
    pass


class SAVE_AND_BREAK(SAVE_AND_BREAK_TYPE):
    pass


__all__ = (
    'BREAK',
    'SAVE_AND_CONTINUE',
    'SAVE_AND_BREAK',
)
