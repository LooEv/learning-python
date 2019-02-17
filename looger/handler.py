import logging
import logging.handlers
import sys
import traceback

from pymongo import MongoClient
from looger.config import DEFAULT_FORMATTER
from utils.commons import camel_case_2_underscore_case

log_handlers = {}


def log_handler(cls_or_func):
    hdr_name = camel_case_2_underscore_case(cls_or_func.__name__)
    log_handlers[hdr_name] = cls_or_func
    return cls_or_func


@log_handler
def stream_logging_handler(**kwargs):
    sh = logging.StreamHandler(kwargs.get('stream', sys.stdout))
    sh.setLevel(kwargs.get('log_level', 'debug').upper())
    sh.setFormatter(kwargs.get('formatter', DEFAULT_FORMATTER))
    return sh


@log_handler
def file_logging_handler(**kwargs):
    log_level = kwargs.pop('log_level', 'debug').upper()
    formatter = kwargs.pop('formatter', DEFAULT_FORMATTER)
    fh = logging.FileHandler(**kwargs)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    return fh


@log_handler
def time_rotating_file_logging_handler(**kwargs):
    log_level = kwargs.pop('log_level', 'debug').upper()
    formatter = kwargs.pop('formatter', DEFAULT_FORMATTER)
    time_rotating_hdr = logging.handlers.TimedRotatingFileHandler(**kwargs)
    time_rotating_hdr.setLevel(log_level)
    time_rotating_hdr.setFormatter(formatter)
    return time_rotating_hdr


@log_handler
class MongodbLoggingHandler(logging.Handler):
    def __init__(self, host='localhost', port=27017, **kwargs):
        super().__init__()
        self.client = MongoClient(host, port, serverSelectionTimeoutMS=2000)
        db_name = kwargs.get('db_name', 'log')
        collection_name = kwargs.get('collection_name', 'msg')
        self.db = self.client.get_database(db_name)
        self._emitter = self.db.get_collection(collection_name)
        self.setLevel(kwargs.get('log_level', 'debug').upper())
        self.setFormatter(kwargs.get('formatter', DEFAULT_FORMATTER))

    def emit(self, record):
        try:
            self._emitter.insert({'msg': record.msg})
        except Exception:
            traceback.print_exc()
