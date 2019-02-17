import time
from random import choice, randint, sample
from string import ascii_uppercase, ascii_lowercase

from utils.coroutine import coroutine


class Consumer:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Consumer[{}]\t'.format(self.name)


@coroutine
def gen_consumer_name():
    flag = ''
    while 1:
        if flag is None:
            break
        last_name = choice(ascii_uppercase)
        first_name = sample(ascii_lowercase, randint(2, 3))
        name = '{} {}'.format(last_name, ''.join(first_name))
        flag = yield name


def go_to_supermarket():
    print('supermarket is opening')
    names_provider = gen_consumer_name()
    while 1:
        name = names_provider.send('')
        consumer = Consumer(name)
        print(str(consumer) + 'is shopping')
        time.sleep(1)


# go_to_supermarket()
import wrapt
