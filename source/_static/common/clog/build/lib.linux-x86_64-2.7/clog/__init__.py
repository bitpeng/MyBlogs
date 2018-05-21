#!/usr/bin/env python
# coding:utf-8

"""
- LOG_DEBUG 输出调试信息到 /smbshare/debug_info.log 文件
- LOG_STACK 输出函数调用栈到 /smbshare/call_stack.log 文件
"""

import log

__all__ = ["LOG_DEBUG", "LOG_STACK", "DEBUG_LOG", "STACK_LOG"]

LOG_DEBUG = log.LOG_DEBUG
LOG_STACK = log.LOG_STACK
LOG_EXCEPTION = log.LOG_EXCEPTION

DEBUG_LOG = log.LOG_DEBUG
STACK_LOG = log.LOG_STACK
#LOG_EXCEPTION = log.LOG_EXCEPTION

