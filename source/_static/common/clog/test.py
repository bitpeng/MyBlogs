#!/usr/bin/env python

from log import LOG_DEBUG

def _test():
    LOG_DEBUG("aaaa", bb=2, cc=3)
    LOG_DEBUG('test', aa='234', d={'1':2})

if __name__ == "__main__":
    _test()
