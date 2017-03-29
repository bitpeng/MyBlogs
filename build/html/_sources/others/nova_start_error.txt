.. _nova_start_error:


Nova服务无法启动,日志,权限和异常处理
#######################################


.. contents:: 目录

--------------------------

最近遇到云平台服务无法通过service命令启动，而使用python方式在命令行启动则没有问题。
该问题涉及的点特别的杂，当然也跟相关代码异常处理没有遵循正确实践相关！现在对相关的问题和知识点做个记录。

**特别说明：以下所有的测试都是基于Ubuntu-14.04 LTS版本！**


问题及现象
===========

原来自己在分析nova项目代码时，对代码进行了某些修改。结果，nova相关组件无法启动，但是通过命令行可以正常启动。

.. figure:: /_static/images/nova_scheduler_cannot_start.png
   :scale: 100
   :align: center

   service命令无法启动nova-scheduler

.. figure:: /_static/images/cli_nova_sche_start.png
   :scale: 100
   :align: center

   命令行方式直接启动，正常！

解决方案
========

这个问题自己一直在尝试解决，定位日志，单步等各种方式。都没有成功！最后不了了之。

一次偶然的机会，向同事提起该问题。他帮忙定位一番后，发现是日志文件权限问题导致无法启动。

.. figure:: /_static/images/nova_log_permission.png
   :scale: 100
   :align: center

   nova-\*.log权限

显然，问题原因是自己分析nova时，把某些日志删掉，然后用root创建了同名文件。
而nova服务用service命令启动时，是使用的nova用户，没有权限写log日志文件。因此导致服务启动失败！

.. figure:: /_static/images/init_nova_sche_conf.png
   :scale: 100
   :align: center

   /etc/init/nova-scheduler.conf文件

原来自己分析过 ``service`` 命令源码，使用service命令启动服务，只不过是对/etc/init/nova-scheduler.conf的包装，
最终还是使用该配置文件启动服务。可以看出，service命令启动的服务，user是nova。

.. figure:: /_static/images/nova_process.png
   :scale: 100
   :align: center

   nova服务进程列表

根据进程列表信息，直接通过命令行启动服务，使用的root用户，因此不会发生权限问题！
而service命令启动的服务，用户是nova，无权限写root用户log，因此启动失败。

针对该权限问题，可以通过如下两种方式：

- 使用chmod命令修改权限

  ::

    chmod 666 /var/log/nova-scheduler.log

- 使用chown命令修改文件所有者和组为nova

  ::

    chown nova:nova /var/log/nova-scheduler.log

异常处理实践
============

为什么看似简单的问题，而日志里面没有任何记录呢？因为nova-scheduler无法写日志，
无法通过nova-scheduler.log定位出原因。更糟糕的是，由于现有代码的异常处理方式，
使得所有的错误和异常均被吞掉，只有简单的提示服务停止信息！

.. figure:: /_static/images/bad_except_handler.png
   :scale: 100
   :align: center

   糟糕的异常处理实践

这种方式修改了所有服务入口，并且在服务终止后在syslog中打印服务终止信息，但是这种方式，
使得真正出问题的异常信息都被忽略掉，反而加大了定位问题的难度！

.. figure:: /_static/images/catch_exception.png
   :scale: 100
   :align: center

   捕获异常

然后再次重启服务试一试，异常信息一目了然，因此定位问题就很简单了！

.. figure:: /_static/images/exception_info.png
   :scale: 100
   :align: center

   syslog日志异常信息

Linux Log
==========

另外，在折腾这个问题的过程中，我还发现一些有趣的现象。

daemon.log日志
+++++++++++++++

首先，Python Logging模块增加syslog handler之后，异常信息不光会记录下/var/log/syslog中，
其他的一些日志文件也会有相关日志。如：/var/log/error；/var/log/daemon.log等。

.. figure:: /_static/images/daemon_log.png
   :scale: 100
   :align: center

.. figure:: /_static/images/error_log.png
   :scale: 100
   :align: center

原来，以service命令启动的服务，实际上一个守护进程，因此出错信息会记录在/var/log/daemon.log文件中！

upstart日志
+++++++++++

其次，部分相关日志信息还会记录进/var/log/upstart/<file>.log中，经过研究，发现有两类日志会记录相应upstart日志中。
下面以nova-scheduler为例进行说明：

- nova-scheduler进程正常产生的日志，应该写进nova-scheduler.log文件中，由于没有写权限，日志会写进/var/log/upstart/nova-scheduler.log中。

- 进程产生异常后，一直进行异常回溯都没有被捕获，那么异常信息就会写入/var/log/upstart/<file>.log中。

比如heat-api服务，服务启动时尝试打开/var/log/heat/heat.log，没有权限，发生异常，异常回溯直到退出都没有被捕获，
因此最后把异常信息写进了/var/log/upstart/heat-api.log文件中！

.. figure:: /_static/images/upstart_heat_log.png
   :scale: 100
   :align: center

   upstart日志文件

日志是一个重要的主题，有时间抽空好好研究Linux平台的日志系统！
