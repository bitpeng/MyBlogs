.. _OpenStack_debug:


########################
OpenStack 调试
########################


.. contents:: 目录

--------------------------

这里简要把自己分析、跟踪、调试OpenStack组件所用到的方法记录下来。
主要参考了网友 `koala bear` 的博文 `OpenStack调试`_ ，在此表示感谢！

.. _`OpenStack调试`: http://wsfdl.com/openstack/2013/08/28/%E8%B0%83%E8%AF%95OpenStack.html


日志
========

``OpenStack logging`` 模块是在 ``python logging`` 基础之上做了封装，使用简单，以 nova 为例，首先需要导入相关代码文件，获取日志句柄后，即可往该句柄写入日志信息。

::

    from nova.openstack.common import log as logging

    LOG = logging.getLogger(__name__)
    LOG.debug("Print log.")

如果文件中已经导入日志模块和获取日志句柄，直接使用该句柄即可。
OpenStack logging 模块提供了丰富的和日志相关的配置项，详情请见 logging config options。

nova组件的默认日志等级是 ``INFO`` ，我们可以开启 ``--debug`` 选项，然后重启服务，
可以看到更详细的日志信息。

有时间，得好好看看 nova.openstack.common.log.py 模块的源码，功能真的很强大!

::

    cd /usr/bin
    ps -ef | grep nova-conductor
    # 然后进程的参数信息，重启服务，开启--debug 选项！
    ./nova-conductor --debug --config-file=/etc/nova/nova.conf
    tail -f /var/log/nova/nova-conductor.log

此外还可以使用 ``nohup`` 命令，将日志输出到自己想要的文件：

::

	cd /usr/bin
	nohup nova-conductor --debug --config-file=/etc/nova/nova.conf > /smbshare/nova-conductor.log 2>&1

**自己添加 LOG 信息：**

假如自己要查看某些变量的信息，可以使用如下方式：

- 添加  ``LOG.debug("+++===+++ arg: %s", arg)`` ，假如模块还没有获取日志句柄，自己就先创建！
- 重启相应服务，开启 ``--debug`` 选项。否则自己添加的日志信息不会记录！
- 然后根据 +++===+++ 过滤：

  ::

    cd /var/log/nova;
    fgrep "+++===+++" . -rn
    # 或者用这种方式
    tail -f /var/log/nova/nova-conductor.log | fgrep "+++===+++"


pdb/ipdb
=========

pdb 是 python 自带的库，它支持设置断点、单步调试源码、查看当前代码、
查看 stack 片段和动态修改变量的值等功能，根据个人经验，使用 pdb 调试 OpenStack
使用到的主要命令包括：

::

    b 10
    b /usr/lib/python2.7/dist-packages/nova/virt/libvirt/driver.py:6046 # 设置断点
    b    # 列出断点
    cl 2 # 删除第二个断点
    c # 继续执行程序直到下一个断点
    n # 继续执行下一行代码
    l # 列出当前代码
    p # 打印变量信息
    pp locals() # 美观打印
    s # 进入函数，该选项对于跨模块调试非常有用！
    r # 执行代码直到从当前函数返回
    q # 退出调试
    a # 列出函数所有参数
    ctrl + c # 重新开始调试
    restart  # 重新开始调试
    <enter>  # 重复上条命令

set_trace
++++++++++

使用该方法时，需在断点处加入以下代码：

::

    import pdb; pdb.set_trace()

以调试 nova 创建虚拟机为例，在 API 入口处加入上行代码：

::

    @wsgi.response(202)
    @wsgi.serializers(xml=FullServerTemplate)
    @wsgi.deserializers(xml=CreateDeserializer)
    def create(self, req, body):
        """Creates a new server for a given user."""

        # 加入此行代码
        import pdb; pdb.set_trace()

        if not self.is_valid_body(body, 'server'):
            raise exc.HTTPUnprocessableEntity()

        context = req.environ['nova.context']
        server_dict = body['server']
        password = self._get_server_admin_password(server_dict)
        ......

由于 pdb 是基于命令行的调试，因此，需要在命令行中重启相应服务，然后创建
虚拟机时执行到该函数就会进入命令行调试模式：

::

    cd /usr/bin
    ps -ef | grep nova-api
    ./nova-api --debug --config-file=/etc/nova/nova.conf


直接使用 pdb 模块参数
+++++++++++++++++++++

无论是日志还是 pdb.set_trace 方法，均需要修改源代码，有没有一种方
法不需要改动文件呢？答案是肯定的，pdb 还提供了另外一种调试模式：

::

    $ python -m pdb debug_file.py

以调试 nova 服务启动为例，步骤如下：

::

    python -m pdb /usr/bin/nova-conductor --debug --config-file=/etc/nova/nova.conf

    # 设置断点 b file_name.py:line
    (pdb) b /usr/lib/python2.6/site-packages/nova/api/openstack/compute/servers.py:781

    # 按 c 运行程序，当收到创建虚拟机请求时，便会进入断点
    (pdb) c

.. figure:: /_static/images/pdb_breakpoint.png
   :scale: 100
   :align: center

   设置跨文件断点


.. error::
    **更新1：**

    `(错误描述): 经过测试，设置跨文件断点，执行时并不会在断点处中断。
    看来跨文件调试，还是得使用 s 命令，或者使用 pdb.set_trace !`

    **更新2：**

    跨文件设置断点，只能在直接 import 的模块设置断点，而不能是连接文件！

    ::

        root@allinone-v2:/var/log/nova# ll /usr/lib/python2.7/dist-packages/nova -d
        lrwxrwxrwx 1 root root 20 Nov 28 13:25 /usr/lib/python2.7/dist-packages/nova -> /opt/cecgw/csmp/nova/

    ::

        root@allinone-v2:/var/log/nova# python -m pdb /usr/bin/nova-conductor --config-file=/etc/nova/nova.conf
        > /usr/bin/nova-conductor(5)<module>()
        -> import sys
        (Pdb) b /usr/lib/python2.7/dist-packages/nova/cmd/conductor.py:45
        Breakpoint 1 at /usr/lib/python2.7/dist-packages/nova/cmd/conductor.py:45
        (Pdb) b /opt/cecgw/csmp/nova/cmd/conductor.py:40
        Breakpoint 2 at /opt/cecgw/csmp/nova/cmd/conductor.py:40
        (Pdb) c
        2016-12-21 14:41:55.005 13939 ERROR nova.cmd.conductor [-] +++===+++ conductor.topic:conductor
        > /usr/lib/python2.7/dist-packages/nova/cmd/conductor.py(45)main()
        -> LOG.error("+++===+++ conductor.manager:%s"%CONF.conductor.manager)
        (Pdb) list
         40         objects.register_all()
         41     
         42         gmr.TextGuruMeditation.setup_autorun(version)
         43     
         44         LOG.error("+++===+++ conductor.topic:%s"%CONF.conductor.topic)
         45 B->     LOG.error("+++===+++ conductor.manager:%s"%CONF.conductor.manager)
         46         server = service.Service.create(binary='nova-conductor',
         47                                         topic=CONF.conductor.topic,
         48                                         manager=CONF.conductor.manager)
         49         LOG.error("+++===+++ conductor: before service.start")
         50         LOG.error("+++===+++ conductor.workers: %s"%CONF.conductor.workers)
        (Pdb) 

    .. figure:: /_static/images/pdb_bk2.png
       :scale: 100
       :align: center

       设置跨文件断点

    可以看到，这里我设置了两个断点，两者实际是一个文件，其中：
    ``/usr/lib/python2.7/dist-packages/nova/cmd/conductor.py`` 是 
    ``/opt/cecgw/csmp/nova/cmd/conductor.py`` 的链接。可以看到，
    执行时，pdb 明显跳过了 ``/opt/cecgw/csmp/nova/cmd/conductor.py:40``
    的断点，因为 import 时使用的是 sys.path 中指定的路径！


命令行debug模式
===============

OpenStack每一个服务都提供的是标准的REST-API接口，如果我们想查看查看某个api的执行细节，
可以通过命令行开启debug模式，查看比较详细的REST-API执行细节。

::

    ceilometer --debug sample-list -m mem.max -l 10
    nova --debug list


使用自己编写的调试设施
=======================

nova 组件日志是根据进程，分别输出到 nova-api.log，nova-scheduler.log 等文件。
假如我们自己添加一些调试信息，那么调试信息也会分散到上述不同文件，并和系统原来
众多的日志混合在一起，查看起来非常不方便。

在充分了解Python和nova日志设施后，完全可以添加自己的filehandler。参考 :ref:`Python logging 模块<log_summary>` ，可以使用该日志包记录日志，然后通过 ``LOG_DEBUG()`` 添加的日志信息都输出到 /smbshare/csq.log 文件。很方便！

另外，nova各组件间，调用和跳转关系比较复杂，为此，自己也维护了一个工具设施 ``LOG_STACK`` ，可以用来很方便
的查看函数调用栈。并格式化输出到文件 call_stack.log，如下图所示；


.. figure:: /_static/images/call_stack1.png
   :scale: 100
   :align: center

   build_instance 函数调用栈


---------------------

参考
=====

.. [#] http://wsfdl.com/openstack/2013/08/28/%E8%B0%83%E8%AF%95OpenStack.html
.. [#] https://www.ibm.com/developerworks/cn/linux/l-cn-pythondebugger/
.. [#] https://docs.python.org/2/library/pdb.html
