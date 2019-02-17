import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class BiuBiuBiu:
    def __init__(self, max_process_num=0, max_thread_num=0):
        if max_process_num > 0 and max_thread_num > 0:
            raise ...
        if max_process_num == max_thread_num == 0:
            raise ...

        if max_process_num:
            self._process_pool = ProcessPoolExecutor(max_process_num)
        else:
            self._process_pool = None

        if max_thread_num:
            self._thread_pool = ThreadPoolExecutor(max_thread_num)
        else:
            self._thread_pool = None
        self.tasks_list = []

    def add_task(self, func, *args, **kwargs):
        self.tasks_list.append((func, args, kwargs))

    def run(self):
        if self._process_pool:
            pool = self._process_pool
        else:
            pool = self._thread_pool
        results = []
        with pool as executor:
            futures = []
            for task in self.tasks_list:
                func, args, kwargs = task
                futures.append(executor.submit(func, *args, **kwargs))
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        return results


if __name__ == '__main__':
    import time

    def tasks(n):
        print('{}'.format(n))
        time.sleep(2)
        print('{}'.format(n))

    biu = BiuBiuBiu(max_thread_num=4)
    biu.add_task(tasks, 2)
    biu.add_task(tasks, 5)
    biu.add_task(tasks, 1)
    biu.run()

######################################################################
######################################################################

from queue import Queue
from threading import Thread


class asynchronous(object):
    def __init__(self, func):
        self.func = func

        def threaded(*args, **kwargs):
            self.queue.put(self.func(*args, **kwargs))

        self.threaded = threaded

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def start(self, *args, **kwargs):
        self.queue = Queue()
        thread = Thread(target=self.threaded, args=args, kwargs=kwargs)
        thread.start()
        return asynchronous.Result(self.queue, thread)

    class NotYetDoneException(Exception):
        def __init__(self, message):
            self.message = message

    class Result(object):
        def __init__(self, queue, thread):
            self.queue = queue
            self.thread = thread

        def is_done(self):
            return not self.thread.is_alive()

        def get_result(self):
            if not self.is_done():
                raise asynchronous.NotYetDoneException('the call has not yet completed its task')

            if not hasattr(self, 'result'):
                self.result = self.queue.get()

            return self.result


if __name__ == '__main__':
    # sample usage
    import time


    @asynchronous
    def long_process(num):
        time.sleep(10)
        return num * num


    result = long_process.start(12)

    for i in range(20):
        print(i)
        time.sleep(1)

        if result.is_done():
            print("result {0}".format(result.get_result()))

    result2 = long_process.start(13)

    try:
        print("result2 {0}".format(result2.get_result()))
    except asynchronous.NotYetDoneException as ex:
        print(ex.message)
