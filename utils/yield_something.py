import time
from utils.coroutine import coroutine


@coroutine
def time_interval():
    start_time = time.time()
    while 1:
        end_time = time.time()
        interval = end_time - start_time
        start_time = end_time
        yield interval


def read_lines():
    my_timer = time_interval()
    time.sleep(1)
    # time.sleep(2)
    # time.sleep(5)
    print(next(my_timer))
    time.sleep(5)
    print(next(my_timer))


read_lines()
