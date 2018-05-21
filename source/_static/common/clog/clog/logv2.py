#!/usr/bin/env python
# coding:utf-8

import logging
import sys
import os
import time


_LOG_NAME = 'CSQ_LOG'

def _getStackLog(filename="/smbshare/csq.log", mode='a'):
    log = logging.getLogger("stack_log")
    log.propagate = 0
    log.setLevel(logging.DEBUG)

    # 增加文件 handler
    fh = logging.FileHandler(filename, mode=mode)
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)
    return log

stack_log = _getStackLog()


def _getLog(name=_LOG_NAME, filename="/smbshare/csq.log", mode='a'):
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
    return log

LOG = _getLog(_LOG_NAME)


#def LOG_DEBUG(*a, **ka):
def LOG_DEBUG(*a, **ka):
    s_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    pid = os.getpid()
    try:
        raise Exception
    except:
        # print "exc_info", sys.exc_info()
        f = sys.exc_info()[2].tb_frame.f_back
    co_filename = f.f_code.co_filename
    co_filename = os.path.abspath(co_filename)

    prefix = "===== [%s] [pid=%s]" % (s_time, pid)
    sufix = "[## %s:%s:%s]" % (co_filename, f.f_code.co_name, f.f_lineno)

    if a and ka:
        LOG.debug("%s [-] %s,  %s,  %s" % (prefix, a, ka, sufix))
    elif ka:
        LOG.debug("%s [-] %s,  %s" % (prefix, ka, sufix))
    else:
        LOG.debug("%s [-] %s,  %s" % (prefix, a, sufix))

def LOG_STACK(log=False):
    import inspect; stack = inspect.stack()
    if log:
        LOG_DEBUG(stack=stack, len=len(stack))

    s_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    pid = os.getpid()
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    co_filename = f.f_code.co_filename
    co_filename = os.path.abspath(co_filename)

    prefix = "[%s] [pid=%s] [-]" % (s_time, pid)
    sufix = "[%s:%s:%s]" % (co_filename, f.f_code.co_name, f.f_lineno)

    #f = open('/smbshare/csq.log', 'a')
    #f.write("\n\n%s\n" % ('<' * 80))
    #f.write("%s CALL STACK IN: \n%s\n\n" %(prefix, sufix))
    ##s = [i[1:] for i in reversed(stack[1:])]
    #s = [str(i[1:]) for i in reversed(stack)]
    ## 读写文件N次，那种方式性能更高待测试！
    ## 经测试，执行10000次该函数大约平均耗时6s。
    ## 由于这种方式是非连续写，可能会发生截断现象。截断现象很少见，但是还是有可能发生！
    ##for i in s:
    ##    f.write("%s\n" % i)
    ## 读写文件一次, 该函数执行10000次耗时6.2s。
    #f.write("\n".join(s))
    #f.write("\n%s\n\n" % ('>' * 80))
    s = ["++ %s" % str(i[1:]) for i in reversed(stack)]
    #s = ["++ %s" % str(i[1:]) for i in reversed(stack)]
    begin = "\n\n%s\n" % ('<' * 80)
    caller_func = "%s call stack in: \n%s\n\n" %(prefix, sufix)
    call_stack = "\n".join(s)
    end = "\n%s\n\n" % ('>' * 80)
    #f.write("%s%s%s%s" % (begin, caller_func, call_stack, end))
    stack_log.debug("%s%s%s%s" % (begin, caller_func, call_stack, end))

if __name__ == "__main__":
    LOG_DEBUG(1, 2, "ab", ["a", "b"])
    LOG_DEBUG("hello, world!", a=1, b=2, c=3)
