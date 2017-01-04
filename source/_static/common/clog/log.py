#!/usr/bin/env python
#coding:utf-8

import logging
import sys
import os

_LOG_NAME = 'CSQ_LOG'

def _getLog(name=_LOG_NAME, filename="/smbshare/csq.log", mode='w'):
#def _getLog(name=_LOG_NAME, filename="/smbshare/csq.log", mode='a'):
    # 保证获取到的 logger 不是全局 root logger
    if not name:
        name = _LOG_NAME
    log = logging.getLogger(name)

    # 日志消息不传递给父 logger 进行处理。
    log.propagate = 0
    log.setLevel(logging.DEBUG)

    # 增加文件 handler
    fh = logging.FileHandler(filename, mode=mode)
    fh.setLevel(logging.DEBUG)

    # 增加标准输出流 handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    log.addHandler(fh)
    log.addHandler(ch)
    #print "log_name is: ", log.name
    return log

LOG = _getLog(_LOG_NAME)


def LOG_DEBUG(*a, **ka):
    try:
        raise Exception
    except:
        #print "exc_info", sys.exc_info()
        f = sys.exc_info()[2].tb_frame.f_back
    co_filename = f.f_code.co_filename
    co_filename = os.path.abspath(co_filename)

    if a and ka:
        LOG.debug("+++===+++ [-] %s,  %s,  [###] %s:%s:%s"%(a, ka, co_filename, f.f_code.co_name, f.f_lineno))
    elif ka:
        LOG.debug("+++===+++ [-] %s,  [###] %s:%s:%s"%(ka, co_filename, f.f_code.co_name, f.f_lineno))
    else:
        LOG.debug("+++===+++ [-] %s,  [###] %s:%s:%s"%(a, co_filename, f.f_code.co_name, f.f_lineno))


if __name__ == "__main__":
    LOG_DEBUG(1, 2, "ab", ["a", "b"])
    LOG_DEBUG("hello, world!", a=1, b=2, c=3)
