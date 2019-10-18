import random


def get_random_code():
    return 'R%d' % int(random.random() * 10 ** 10)
