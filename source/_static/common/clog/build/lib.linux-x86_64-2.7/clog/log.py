#!/usr/bin/env python
# coding:utf-8

import logging
import sys
import os
import time


_LOG_NAME = 'CSQ_LOG'

def _getStackLog(filename="/smbshare/call_stack.log", mode='a'):
    log = logging.getLogger("STACK_LOG")
    log.propagate = 0
    log.setLevel(logging.DEBUG)

    fh = logging.FileHandler(filename, mode=mode)
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)
    return log

STACK_LOG = _getStackLog()

def _getExceptLog(filename="/smbshare/except.log", mode='a'):
    log = logging.getLogger("EXCEPT_LOG")
    log.propagate = 0
    log.setLevel(logging.DEBUG)

    fh = logging.FileHandler(filename, mode=mode)
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)
    return log

EXCEPT_LOG = _getExceptLog()

def LOG_EXCEPTION(e):
    #print e
    EXCEPT_LOG.info('\n\nException Catched!')
    EXCEPT_LOG.exception(e)


def _getLog(name=_LOG_NAME, filename="/smbshare/debug_info.log", mode='a'):
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

    import threading
    nowthread = threading.currentThread()

    prefix = "===== [%s] [pid=%s] [tid=%s, tidname=%s]" % (s_time, pid, hex(nowthread.ident), nowthread.name)
    sufix = "[## %s:%s:%s]" % (co_filename, f.f_code.co_name, f.f_lineno)

    if a and ka:
        LOG.debug("%s [-] %s,  %s,  %s" % (prefix, a, ka, sufix))
    elif ka:
        LOG.debug("%s [-] %s,  %s" % (prefix, ka, sufix))
    else:
        LOG.debug("%s [-] %s,  %s" % (prefix, a, sufix))

def LOG_STACK(log=False):
    '''该函数尝试输出函数的调用栈到日志文件 /smbshare/call_stack.log
    由于inspect.stack() 函数返回的列表格式不便于方便的查看函数调用栈，
    因此，我会输出格式进行了一定的美化。

    输出信息格式如下示例：
    <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    [2017-01-15 10:54:54] [pid=61749] [-] call stack in:-
    [/usr/local/lib/python2.7/dist-packages/clog/test.py:_test:11]

    ++ ('test.py', 14, '<module>', ['    _test()\n'], 0)
    ++ ('test.py', 11, '_test', ['    LOG_STACK()\n'], 0)
    ++ ('/usr/local/lib/python2.7/dist-packages/clog/log.py', 83, 'LOG_STACK', ['    import inspect; stack = inspect.stack()\n'], 0)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    - 第一行，调用LOG_STACK函数的时间，进程pid；
    - 第二行，调用LOG_sTACK函数的源码位置。
    - 调用函数的调用栈信息；

    使用时，只需要简单的调用该函数即可。另外，它还有一个log参数，假如
    该值为真，会把非格式化的调用栈列表输出到日志文件 /smbshare/debug_info.log

    变更历史：
    1. 原来自己初次编写该函数时，直接使用open函数打开文件，然后进行write操作。
    2. 但是，由于该函数可能会被多个进程调用，因此涉及到多个进程写文件的问题。
       可能会发生写覆盖、输出混合到一起等现象，因此尝试使用I/O锁。
    3. 参考logging模块，最后决定直接使用Log + filehandller 方式输出到文件(
       filehandler维护了I/O锁)。此时，上述两个问题已经消失。
    '''
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

    s = ["++ %s" % str(i[1:]) for i in reversed(stack)]
    #s = ["-> %s" % str(i[1:]) for i in reversed(stack)]
    begin = "\n%s\n" % ('<' * 80)
    caller_func = "%s call stack in: \n%s\n\n" %(prefix, sufix)
    call_stack = "\n".join(s)
    end = "\n%s\n" % ('>' * 80)
    STACK_LOG.debug("%s%s%s%s" % (begin, caller_func, call_stack, end))

if __name__ == "__main__":
    LOG_DEBUG(1, 2, "ab", ["a", "b"])
    LOG_DEBUG("hello, world!", a=1, b=2, c=3)
