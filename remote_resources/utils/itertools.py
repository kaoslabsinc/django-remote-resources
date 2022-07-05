from itertools import islice


def limit_iterator(iterator, max_pages):
    if max_pages:
        iterator = islice(iterator, max_pages)
    return iterator
