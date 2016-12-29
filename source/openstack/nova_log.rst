.. _nova_log:


########################
OpenStack 日志模块分析
########################

**date: 2016-12-29 14:00**

.. contents:: 目录

--------------------------

日志是OpenStack开发调试、运维等操作的重要参考。OpenStack log 模块在
Python logging 模块的基础之上进行封装，并增加一些更丰富的特性。这篇
文章尝试对 OpenStack log 模块进行彻底的分析！首先可以参考python 官网
库参考 logging 模块和 `Python logging howto，python logging cookbook` ，
对 logging模块的用法和特性有个基本的了解。也可以参考 :ref:`logging模块总结<log_summary>`。

下面以 nova-scheduler 启动为例，讲解 nova-scheduler 服务的日志设施。这里是 nova-scheduler
服务入口：

:file:`nova/cmd/scheduler.py`
::

    def main():
        config.parse_args(sys.argv)
        logging.setup("nova")


命令行参数解析完成后，执行logging.setup("nova") 语句，
进行日志设置，接下来所有的源码基本都源于 :file:`nova/openstack/common/log.py` 文件，
不是该文件的源码会特别标出。

:file:`nova/openstack/common/log.py`
::

    def setup(product_name, version='unknown'):
        """Setup logging."""
        if CONF.log_config_append:
            _load_log_config(CONF.log_config_append)
        else:
            _setup_logging_from_conf(product_name, version)
        sys.excepthook = _create_logging_excepthook(product_name)

log_config_append 是 :file:`nova/openstack/common/log.py` 模块注册的命令行选项，默认为 Flase;
于是执行 :func:`_setup_logging_from_conf` 函数设置日志信息！

.. note::

    根据 :ref:`oslo.config 库学习 <oslo_cfg>` 可知，实际上参数解析时 ``CONF()`` 已经
    通过 ``project="nova"`` 参数加载了配置文件 /etc/nova/nova.conf 。
    因此有些配置项的值从该配置文件中取得。

接下来的 :func:`_setup_logging_from_conf` 函数有点长，我们来慢慢看：

::

    def _setup_logging_from_conf(project, version):
        # 这里返回name为None的Logger对象。实际上是返回root logger
        log_root = getLogger(None).logger
        for handler in log_root.handlers:
            log_root.removeHandler(handler)
        
经测试，当 name 为None或者""(空字符串)调用 getLogger()时，返回root logger。

.. 然后root logger的设置，都会被child logger继承，除非 child logger显示设置。

::

    def getLogger(name='unknown', version='unknown'):
        if name not in _loggers:
            _loggers[name] = ContextAdapter(logging.getLogger(name),
                                            name,
                                            version)
        return _loggers[name]
    
getLogger 函数返回的是 logging Adapter 对象，允许我们重写 process 函数，
从而在Formatter中添加自定义字段和格式信息。

继续返回到 _setup_logging_from_conf 函数分析：

::

    logpath = _get_log_file_path()
    if logpath:
        filelog = logging.handlers.WatchedFileHandler(logpath)
        log_root.addHandler(filelog)

    if CONF.use_stderr:
        streamlog = ColorHandler()
        log_root.addHandler(streamlog)

    elif not logpath:
        # pass sys.stdout as a positional argument
        # python2.6 calls the argument strm, in 2.7 it's stream
        streamlog = logging.StreamHandler(sys.stdout)
        log_root.addHandler(streamlog)

    if CONF.publish_errors:
        try:
            handler = importutils.import_object(
                "nova.openstack.common.log_handler.PublishErrorsHandler",
                logging.ERROR)
        except ImportError:
            handler = importutils.import_object(
                "oslo.messaging.notify.log_handler.PublishErrorsHandler",
                logging.ERROR)
        log_root.addHandler(handler)

这处代码尝试对root logger设置 fileHandler, StreamHandler等。

获取fileHandler的方式如下：

尝试根据配置获取日志文件的目录；CONF.log_dir 已经在/etc/nova/nova.conf 中
定义为: ``log_dir=/var/log/nova``；并通过Python 自省获取应用程序名字。然后
将日志目录和应用程序名称(eg: nova-scheduler)拼接组成日志路径。

通过Python自省获取应用程序名称。

::

    def _get_binary_name():
        #stack = inspect.stack()[-1][1]
        stack = inspect.stack()
        b = os.path.basename(stack[-1][1])
        print ("+++===+++ stack: %s"%stack)
        return b

::

    +++===+++ stack: [(<frame object at 0x7f7011b2db00>, '/usr/lib/python2.7/dist-packages/nova/openstack/common/log.py', 211, '_get_binary_name', ['    stack = inspect.stack()\n'], 0), 
    (<frame object at 0x7f7011aef620>, '/usr/lib/python2.7/dist-packages/nova/openstack/common/log.py', 230, '_get_log_file_path', ['        binary = binary or _get_binary_name()\n'], 0), 
    (<frame object at 0x29445f0>, '/usr/lib/python2.7/dist-packages/nova/openstack/common/log.py', 498, '_setup_logging_from_conf', ['    logpath = _get_log_file_path()\n'], 0), 
    (<frame object at 0x7f7011b2d938>, '/usr/lib/python2.7/dist-packages/nova/openstack/common/log.py', 432, 'setup', ['        _setup_logging_from_conf(product_name, version)\n'], 0), 
    (<frame object at 0x7f701a5e9d00>, '/usr/lib/python2.7/dist-packages/nova/cmd/scheduler.py', 44, 'main', ['    logging.setup("nova")\n'], 0), 
    (<frame object at 0x7f701ba703e0>, '/usr/bin/nova-scheduler', 40, '<module>', ['        sys.exit(main())\n'], 0)]

将应用程序名称和日志目录拼接，结果返回 "/var/log/nova/nova-scheduler.log" 字符串，
表示完整的日志文件路径。

::

    def _get_log_file_path(binary=None):
        logfile = CONF.log_file
        logdir = CONF.log_dir

        if logfile and not logdir:
            return logfile

        if logfile and logdir:
            return os.path.join(logdir, logfile)

        if logdir:
            binary = binary or _get_binary_name()
            return '%s.log' % (os.path.join(logdir, binary),)

        return None

接下来，对 root logger的每一个handlers对象，设置 Formatter 日志格式。
我在这里加上了 print 语句，打印 root logger 拥有的 handler 对象。

::

    datefmt = CONF.log_date_format
    for handler in log_root.handlers:
        # NOTE(alaski): CONF.log_format overrides everything currently.  This
        # should be deprecated in favor of context aware formatting.
        # add by chenshiqiang
        print "+++===+++ handler.stream:", handler.stream
        # end add
        if CONF.log_format:
            handler.setFormatter(logging.Formatter(fmt=CONF.log_format,
                                                   datefmt=datefmt))
            log_root.info('Deprecated: log_format is now deprecated and will '
                          'be removed in the next release')
        else:
            handler.setFormatter(ContextFormatter(project=project,
                                                  version=version,
                                                  datefmt=datefmt))


.. figure:: /_static/images/handler_stream.png
   :scale: 100
   :align: center

   root logger所拥有的handle对象
  
根据打印信息，可以看到 **root logger 有两个 handler对象。因此符合日志等级的消息，一方面会被
追加到日志文件 /var/log/nova-scheduler.log；还会输出到标准错误流(从命令行启动 nova-scheduler 时)。**

接下来，设置 root logger的日志等级。假如在命令行选项开启 ``--debug`` 或者 ``-d`` 选项
则优先设置 debug 等级， CONF.verbose 在 /etc/nova/nova.conf 中定义，默认为真。
然后设置一些库的默认日志等级。

::

    if CONF.debug:
        log_root.setLevel(logging.DEBUG)
    elif CONF.verbose:
        log_root.setLevel(logging.INFO)
    else:
        log_root.setLevel(logging.WARNING)

    for pair in CONF.default_log_levels:
        mod, _sep, level_name = pair.partition('=')
        logger = logging.getLogger(mod)
        # NOTE(AAzza) in python2.6 Logger.setLevel doesn't convert string name
        # to integer code.
        if sys.version_info < (2, 7):
            level = logging.getLevelName(level_name)
            logger.setLevel(level)
        else:
            logger.setLevel(level_name)

最后，根据 use-syslog 选项，确定是否增加 SysLogHandler，该选项默认关闭。

::

    if CONF.use_syslog:
        try:
            facility = _find_facility_from_conf()
            # TODO(bogdando) use the format provided by RFCSysLogHandler
            #   after existing syslog format deprecation in J
            if CONF.use_syslog_rfc_format:
                syslog = RFCSysLogHandler(address='/dev/log',
                                          facility=facility)
            else:
                syslog = logging.handlers.SysLogHandler(address='/dev/log',
                                                        facility=facility)
            log_root.addHandler(syslog)
        except socket.error:
            log_root.error('Unable to add syslog handler. Verify that syslog'
                           'is running.')

综上，通过 _setup_logging_from_conf 给 root logger增加了2个handlers对象，设置Formatter
格式，和日志层级。

在其他模块中，一般都是通过 ``LOG = logging.getLogger(__name__)`` 返回本模块 logger 对象
(实际上是 ContextAdapter 对象)，然后直接使用 LOG 记录日志信息。请注意，实际上，
**本模块logger(LOG.logger)实际上没有任何handlers对象，但是，由于 logger对象的
propagate 属性(默认为True)，因此会把日志消息"传递" 给每一个父 logger(直到root logger)，
父logger把消息发送到每一个handlers(消息目的地)。**

.. figure:: /_static/images/LOG_handlers.png
   :scale: 100
   :align: center

   打印某模块 logger 的handler对象
   
.. figure:: /_static/images/LOG_handlers_2.png
   :scale: 100
   :align: center

   模块logger handlers为空, 消息最终由 root logger记录进日志文件，并输出到标准错误
