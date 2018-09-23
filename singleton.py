##########################################################################################
# __new__


class Singleton1:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton1, cls).__new__(cls)
            # in python 3.3 and later, can't use a usage like the following
            # cls._instances[cls] = super(Singleton1, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


class TestSon(Singleton1):
    def __init__(self, name):
        print('in __init__, its name is {}'.format(name))


t1 = TestSon('tom')
print(id(t1))
t2 = TestSon('tony')
print(id(t2))
print(hash(t1) == hash(t2))


##########################################################################################
# __call__ using metaclass


class Singleton2(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton2, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TestSon(metaclass=Singleton2):
    def __init__(self, name):
        print('in __init__, its name is {}'.format(name))


t1 = TestSon('tom')
print(id(t1))
t2 = TestSon('tony')
print(id(t2))
