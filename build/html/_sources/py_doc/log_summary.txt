.. _log_summary:


########################
logging 模块总结
########################

**date: 2016-12-28 10:00**

.. contents:: 目录

--------------------------

Python logging 模块是Python重要的日志设施，一直都对这个库的用法似懂非懂，
很多概念也不清晰。今天对该库进行彻底总结。

logging 模块工作模式与要点
===========================

Logger
++++++++

logging 模块使用 :class:`Logger` 操作日志，我们可以使用 ``logging.getLogger(name)`` 返回一个对象。
假如 :func:`getLogger` 的 name参数没有指定，或者 name 参数为假值(eg: None, "", {}等)，那么
该函数将会返回 root :class:`Logger` 全局对象。

以下是 Logger 对象的一些关键属性：

.. attribute:: name

    Logger 对象的名字
    
.. attribute:: level

    记录日志时的最低等级。
    
    子logger写日志时，优先使用本身设置了的level；如果没有设置，则逐层向上级父
    logger查询，直到查询到为止。最极端的情况是，使用rootLogger的默认日志级别logging.WARNING。
    
.. attribute:: propagate

    该属性值非常重要，默认为真。假如为真，那么 Logger 对象会把日志操作依次传递给
    parent logger 对象进行进一步处理。
    
.. attribute: handlers

    日志消息的目的地。

Handler
++++++++

存在多种内置的Handler将log分发到不同的目的地，
或是控制台，或是文件，或是某种形式的stream，或是socket等。一个logger可以
绑定多个handler，例如，一条日志可以同时输出到控制台和文件中。

`A Handler is an object which you attach to a Logger. Whenever the logger has a message to process, it sends the message to all of its handlers. Additionally, Loggers exist in a tree structure, with the aptly named "root" Logger at its root. After sending a message to its Handlers, a Logger may pass it on to its parent in the tree (determined by the Logger instance's propagate attribute).`

关键属性：

.. attribute:: level

    该handler接收日志的最低等级。
    
    Handler 对象的 level 等级和 Logger 对象的日志等级并不矛盾。通过
    设置 Handler 对象的日志等级，我们可以对日志进行更精细的控制，如将
    不同 level 的消息发送到不同的 handler .
    
.. attribute:: formatter

    :class:`Formatter` 对象，记录日志消息时的格式。

通过上面的讲解，我们可以知道 logging 处理的日志的一般步骤：

#. 获取 Logger 对象；
#. 比较消息的等级和 Logger 对象的 level进行日志消息过滤；
#. 将消息发送给 Logger 对象的每一个 handlers；如果 handlers 列表为空，会提示 "no handlers could be found" 信息；
#. 在每一个handler 中，再次根据消息等级和 handler.level 进行消息过滤；并将过滤后的消息发送到对应的目的地。
#. **如果 logger.propagate 为真，依次让 logger.parent 处理日志消息，直到 root logger 或者遇到 logger.propagate
   值为假时停止。**

no handler found提示
=====================

`You've probably come across this message, especially when working with 
3rd party modules. What this means is that you don't have any logging handlers 
configured, and something is trying to log a message. The message has gone all 
the way up the logging hierarchy and fallen off the...top of the chain (maybe I need a better metaphor).`

为了避免该错误，我们一般在对 root logger 执行 basicConfig() 配置，然后其他的 logger 都会继承 root logger.

让我们来看看最简单的代码：

::

    >>> import logging;
    >>> log1 = logging.getLogger()
    >>> log1.warn('aaa')
    No handlers could be found for logger "root"
    >>> logging.warn('log-warn-info')
    WARNING:root:log-warn-info
    >>> log1.name
    'root'
    >>> log1.warn('aaa')
    WARNING:root:aaa


从logging模块的源码我们知道，logging.warn() 实际上使用的是 root logger (logging.py 模块的全局对象)处理日志。
使用log1.warn() 时，由于此时root logger没有任何handler，所以提示 no handlers 消息。

::

    def warning(msg, *args, **kwargs):
        """  
        Log a message with severity 'WARNING' on the root logger.
        """
        if len(root.handlers) == 0:
            basicConfig()
        root.warning(msg, *args, **kwargs)


::

    def basicConfig(**kwargs):

        # Add thread safety in case someone mistakenly calls
        # basicConfig() from multiple threads
        _acquireLock()
        try:
            if len(root.handlers) == 0:
                filename = kwargs.get("filename")
                if filename:
                    mode = kwargs.get("filemode", 'a')
                    hdlr = FileHandler(filename, mode)
                else:
                    stream = kwargs.get("stream")
                    hdlr = StreamHandler(stream)
                fs = kwargs.get("format", BASIC_FORMAT)
                dfs = kwargs.get("datefmt", None)
                fmt = Formatter(fs, dfs)
                hdlr.setFormatter(fmt)
                root.addHandler(hdlr)
                level = kwargs.get("level")
                if level is not None:
                    root.setLevel(level)
        finally:
            _releaseLock()

::

    class StreamHandler(Handler):
        """
        A handler class which writes logging records, appropriately formatted,
        to a stream. Note that this class does not close the stream, as
        sys.stdout or sys.stderr may be used.
        """

        def __init__(self, stream=None):
            """
            Initialize the handler.

            If stream is not specified, sys.stderr is used.
            """
            Handler.__init__(self)
            if stream is None:
                stream = sys.stderr
            self.stream = stream


执行logging.warn()会调用basicConfig(),在这个函数中，root logger 增加了一个目的地为 sys.stderr 的 StreamHandler。
然后再次执行 log1.warn() 时，就把消息输出到标准错误流。


测试代码：

::

    import logging
    from logging import getLogger
    #from nova.openstack.common import log as os_log
    import sys

    #logging.basicConfig(format=logging.BASIC_FORMAT)
    #logging.warn('aa')
    file_handler = logging.FileHandler('file.log', mode="a")
    fmt = logging.Formatter(logging.BASIC_FORMAT)
    file_handler.setFormatter(fmt)
    root_log = getLogger()
    root_log.addHandler(file_handler)
    root_log.warn('root_log warn')

    log1 = getLogger(None)
    log2 = getLogger('')
    #log3 = getLogger('root.a')
    log3 = getLogger('a')
    streamlog = logging.StreamHandler(sys.stdout)
    #colorhdlr = os_log.ColorHandler()
    #log1.addHandler(streamlog)
    log1.addHandler(streamlog)
    #log2.addHandler(streamlog)
    #log2.addHandler(colorhdlr)

    log1.warn('log1 warn')
    log2.warn('log2 warn')
    print root_log.handlers
    for i in root_log.handlers:
        print i,', ', i.stream
        #print "formatter:", i.formatter._fmt
        #print "formatter:", i.formatter._fmt
        if i.formatter:
            print "formatter:", i.formatter._fmt
        else:
            print "formatter is empty"
        print

    print id(log1)
    print id(log2)
    print id(root_log)

    print log1 is log2
    root_log.warn('root_log warn')
    root_log.error('root_log error')

    log3.warn('log3 test warn')
    #print log3.formatter._fmt
    print "log3.handlers:", log3.handlers
    print "type log3:", type(log3)
    print "log3.name:", log3.name


    #log3.addHandler(file_handler)
    #log3.propagate=0
    #print "update log3.handlers:", log3.handlers
    log3.warn('log3 aaaa')

测试结果：

::

    ./test_log.py 
    # 过滤掉标准错误流(sys.stderr)
    ./test_log.py 2>/dev/null
    # 过滤掉标准输出流(sys.stdout)
    ./test_log.py 1>/dev/null
    tail -f file.log


编写自己的日志包
=================

在充分理解了 Python logging 日志设施之后，完全可以编写自己的 log 包装模块

::

    root@allinone-v2:/usr/local/lib/python2.7/dist-packages# tree clog
    clog
    ├── __init__.py
    ├── __init__.pyc
    ├── log.py
    ├── log.pyc
    └── test.py

    0 directories, 5 files

自己编写的log包装模块目录结构如上图所示。

以下是包的代码，并附有简单的注释：

:file:`log.py`

.. literalinclude:: /_static/common/clog/log.py
    :language: python
    :linenos:

:file:`__init__.py`

.. literalinclude:: /_static/common/clog/__init__.py
    :language: python
    :linenos:

:file:`test.py`

.. literalinclude:: /_static/common/clog/test.py
    :language: python
    :linenos:
