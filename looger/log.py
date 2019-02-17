import logging
from collections import Iterable

from looger.handler import log_handlers


class Logger:
    def __init__(self, name=None, log_level='debug', **kwargs):
        assert name is not None, "logger's name is None"
        self._logger = logging.getLogger(name)
        self._log_level = logging.getLevelName(log_level.upper())
        self._logger.setLevel(self._log_level)
        # if log's name has been existed, need to set handlers to emtpy
        # otherwise, some strange things happened ~.~
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
        # you can give some logging handlers you make
        handlers = kwargs.pop('handlers', None)
        if isinstance(handlers, Iterable):
            [self._logger.addHandler(hdr) for hdr in handlers]
        for log_type, config in kwargs.items():
            log_hdr_name = (log_type + '_logging_handler').lower()
            if log_hdr_name in log_handlers:
                hdr = log_handlers.get(log_hdr_name)(**config)
                self._logger.addHandler(hdr)

    def get_logger(self):
        return self._logger

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return getattr(self._logger, name)
