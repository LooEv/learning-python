import socket
from logging import Formatter

LOG_CONFIG = {
    'stream': {
        'log_level': 'debug',
    },
    'file': {
        'log_level': 'info',
        'filename': './my_log',
    },
    # 'time_rotating_file': {
    #     'log_level': 'info',
    #     'filename': './my_log',
    #     'when': 'S',
    #     'interval': 3,
    #     'backupCount': 3,
    # },
    # # 'flume': {
    #     'log_level': 'debug',
    #     'host': 'localhost',
    #     'port': 41416,
    # },
    # 'mongodb': {
    #     'log_level': 'debug',
    #     'host': 'localhost',
    #     'port': 27017,
    #     'db_name': 'log',
    #     'collection_name': 'logs'
    # },
}

host_name = socket.getfqdn(socket.gethostname())
formatter_str = host_name + '||%(asctime)s||%(levelname)s||' \
                            '%(filename)s->%(funcName)s %(lineno)-3d||%(message)s'
DEFAULT_FORMATTER = Formatter(formatter_str)
