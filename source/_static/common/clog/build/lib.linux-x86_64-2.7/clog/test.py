#! /usr/bin/env python

from log import LOG_DEBUG
from log import LOG_STACK
from log import LOG_EXCEPTION
from memoized import memoized


def _test():
    LOG_DEBUG("aaaa", bb=2, cc=3)
    LOG_DEBUG('test', aa='234', d={'1': 2})
    #for i in range(10000):
    LOG_STACK()

#@memoized
def add(p):
    res = []
    res.extend([i for i in range(p)])
    return id(res), res

def test_exception():
    try:
        1/0
    except Exception, e:
        LOG_EXCEPTION(e)


if __name__ == "__main__":
    _test()

    a = 10
    print add(a)
    print add(a)
    print add(10)
    print add(a+a)
    print add(a+a)
    test_exception()
