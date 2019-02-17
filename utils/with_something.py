from contextlib import contextmanager


@contextmanager
def strip_file_lines(*args):
    with open(*args) as _file:
        yield (_line.strip() for _line in _file if _line.strip())


class Attr:
    attr_name = ''
