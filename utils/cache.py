from functools import wraps
from collections import UserDict, Hashable


class Cache(UserDict):
    def __init__(self, func):
        self.func = func
        super().__init__()

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result


def cache(func):
    memo = {}

    @wraps(func)
    def _wrapper(*args):
        res = memo.get(args, None)
        # print(memo)
        if res is not None:
            return res
        else:
            res = func(*args)
            memo[args] = res
        return res

    return _wrapper


@Cache
def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


class Test:
    @cache
    def fib(self, n):
        print('first')
        return n ** 2


class memoized(object):
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        return self.func.__doc__


# @memoized
def fibonacci(n):
    "Return the nth fibonacci number."
    if n in (0, 1):
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# print([fib(i) for i in list(range(10))])

t = Test()
t.fib(5)
t.fib(5)
t.fib(5)
