.. _oslo_cfg:


########################
oslo.config 用法总结
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. contents:: 目录

--------------------------

OpenStack源码中使用了很多的标准库和第三方库，假如不熟悉这些库的用法，分析代码时往往会事倍功半。oslo作为OpenStack的通用组件，在每一个项目中都有用到，现在对子项目 ``oslo.config`` 用法做一个总结！由于oslo.config支持的功能非常的多，因此这里可能只会列出常用的用法。

代码版本为 OpenStack juno！

配置项
=======

::

    import sys
    from oslo.config import cfg
    from oslo.config import types

    PortType = types.Integer(1, 65535)

    disk_list = ['hda 100G', 'hdb 150G', 'hdc 200G']
    disk_opts= [cfg.MultiStrOpt('volume', default=disk_list, help='disk volumes in GB')]

    cli_opts = [
        cfg.StrOpt('host',
                default='119.119.119.119',
                help='IP address to listen on.'),
        cfg.Opt('port',
                type=PortType,
                default=9292,
                help='Port number to listen on.')
    ]


配置项类型
===========

第一种方式是使用 cfg.StrOpt，cfg.IntOpt 等带有类型的参数类；另一种方式是在
初始化 cfg.Opt 时传递 type 参数。oslo.config 支持多种类型！

注册参数
========

::

    # oslo.config 默认维护了一个 ConfigOpts 类型的全局变量 CONF。
    # 注册参数，以及后续获取参数，都是可以通过 CONF。
    CONF = cfg.CONF
    # disk_opts 不是命令行参数，所以假如要覆盖默认值，只能通过配置文件改变！
    # 注册的选项必须是可迭代的！否则会发生错误
    CONF.register_opts(disk_opts)
    CONF.register_cli_opts(cli_opts)

通过命令行指定的参数，一定要通过 :func:`CONF.register_cli_opts` 指定！
而非命令行参数，只能通过配置文件覆盖默认值。

.. note::

    注意，之前代码的注释中，说注册的参数必须是可迭代的。

    这个说法有问题，注册参数，有两类方法，一类是 :func:`register_opt` 和 :func:`register_cli_opt` ；
    还有一类是 :func:`register_opts` 和 :func:`register_cli_opts` 。

    :func:`register_opt` 和 :func:`register_cli_opt` 可以直接注册选项！


参数解析
========

配置文件和命令行参数解析是通过 ``CONF(sys.argv[1:])`` 完成。

::

    if __name__ == '__main__':
        CONF(sys.argv[1:])

        print "volume:", CONF.volume
        print "cli_host:", CONF.host
        print "cli_port:", CONF.port

获取帮助信息
============

.. code-block:: console

    root@allinone-v2:/smbshare# ./test_cfg.py -h
    usage: test_cfg.py [-h] [--config-dir DIR] [--config-file PATH] [--host HOST]
                       [--port PORT] [--version]

    optional arguments:
      -h, --help          show this help message and exit
      --config-dir DIR    Path to a config directory to pull *.conf files from.
                          This file set is sorted, so as to provide a predictable
                          parse order if individual options are over-ridden. The
                          set is parsed after the file(s) specified via previous
                          --config-file, arguments hence over-ridden options in
                          the directory take precedence.
      --config-file PATH  Path to a config file to use. Multiple config files can
                          be specified, with values in later files taking
                          precedence. The default files used are: None.
      --host HOST         IP address to listen on.
      --port PORT         Port number to listen on.
      --version           show program's version number and exit


可以看到，oslo.config 默认具有 --config-file 和 --config-dir 两个
选项，用来从配置文件中获取参数值！


参数分组
========

参数分组，既可以通过 :class:`cfg.OptGroup` 指定，也可以在
注册参数时直接指定分组名字字符串，个人倾向直接使用字符串组名。

::

    CONF.register_opts(disk_opts, 'disk')
    CONF.register_cli_opts(cli_opts, 'cli')


使用分组后，看看帮助信息

.. code-block:: console

    root@allinone-v2:/smbshare# ./test_cfg.py -h
    usage: test_cfg.py [-h] [--config-dir DIR] [--config-file PATH] [--version]
                       [--cli-host CLI_HOST] [--cli-port CLI_PORT]

    optional arguments:
      -h, --help           show this help message and exit
      --config-dir DIR     Path to a config directory to pull *.conf files from.
                           This file set is sorted, so as to provide a predictable
                           parse order if individual options are over-ridden. The
                           set is parsed after the file(s) specified via previous
                           --config-file, arguments hence over-ridden options in
                           the directory take precedence.
      --config-file PATH   Path to a config file to use. Multiple config files can
                           be specified, with values in later files taking
                           precedence. The default files used are: None.
      --version            show program's version number and exit

    cli options:
      --cli-host CLI_HOST  IP address to listen on.
      --cli-port CLI_PORT  Port number to listen on.


可以看到，指定分组后：

- 命令行参数，需要在命令行中通过 ``[分组名]-[参数名]`` 来指定；
- 对于配置文件参数，分组可以通过下面的方式指定，其中分组名和配置文件section名字一致。

  ::

    [disk]
    volume=sda 100GB
    volume=sdb 200GB

    [cli]
    host=0.0.0.0
    port=8080

命令行和配置文件重复指定配置项
==============================

假如在命令行和配置文件中，都指定了配置项，那么后指定的会覆盖先指定的！

.. code-block:: console

    root@allinone-v2:/smbshare# ./test_cfg.py
    volume: ['hda 100G', 'hdb 150G', 'hdc 200G']
    cli_host: 119.119.119.119
    cli_port: 9292
    root@allinone-v2:/smbshare# 
    root@allinone-v2:/smbshare# 
    root@allinone-v2:/smbshare# ./test_cfg.py --config-dir .
    volume: ['sda 100GB', 'sdb 200GB']
    cli_host: 0.0.0.0
    cli_port: 8080
    root@allinone-v2:/smbshare# 
    root@allinone-v2:/smbshare# ./test_cfg.py --config-dir . --cli-host 1.1.1.1
    volume: ['sda 100GB', 'sdb 200GB']
    cli_host: 1.1.1.1
    cli_port: 8080
    root@allinone-v2:/smbshare# ./test_cfg.py --cli-host 1.1.1.1 --config-dir .
    volume: ['sda 100GB', 'sdb 200GB']
    cli_host: 0.0.0.0
    cli_port: 8080

可以看到，假如命令行参数最后指定，就会覆盖配置文件中的相应参数；反过来亦然！

从其他模块导入配置
==================

由于OpenStack项目大，模块多。因此假如可以在部分模块中定义配置项，然后其他模块直接
导入，就会很方便，也方便管理。

oslo.config 支持直接从其他模块中导入配置！可以使用 :meth:`ConfigOpts.import_opt` 实现。

.. method:: ConfigOpts.import_opt(self, name, module_str, group=None)

    :param name: 导入的参数选项名字；
    :param module_str: 带导入配置项所在模块名字字符串；
    :param group: name配置项所在分组；

.. 其中，name参数是导入的选项，module_str 是模块名字字符串，group是name配置项所在分组！

请看下面的例子：

::

    from oslo.config import cfg 

    CONF = cfg.CONF
    CONF.import_opt('volume', 'test_cfg', group='disk')

    print CONF.disk.volume
    print CONF.disk.type
    print CONF.cli.host

导入配置项测试结果:

.. code-block:: console

    root@allinone-v2:/smbshare# python test_import_oslo.py
    disk volume:  ['hda 100G', 'hdb 150G', 'hdc 200G']
    disk type:  ssd
    cli host:  119.119.119.119

导入配置项结果测试在我意料之外，原来，**导入某模块中任意一项，
该模块的所有配置项，都可以直接访问！**
从其他模块导入配置项这种用法在 OpenStack 组件中使用相当广泛!

代码汇总
========

以下是本次测试代码，可以直接复制运行！

test_cfg.py：

.. literalinclude:: /_static/src/test_cfg.py
    :language: python
    :linenos:

配置文件test_oslo.conf：

.. literalinclude:: /_static/src/test_oslo.conf
    :language: shell
    :linenos:

导入测试 test_import_oslocfg.py：

.. literalinclude:: /_static/src/test_import_oslocfg.py
    :language: shell
    :linenos:

补充和更新
===========

对配置项下划线的特殊处理
++++++++++++++++++++++++

**update: 2016/12/25-18-54**

oslo.config.cfg 模块，对配置项名称中下划线进行了特殊处理，这一点要特别注意。

比如我今天在阅读 nova/openstack/common/log.py 代码时，代码中有这么一项：

::

    if CONF.log_config_append:
        xxxx

结果怎么都搜索不到该配置项 ``log_config_append`` , 在 /etc/nova/nova.conf
中也没有该配置项。后来，从文件头部开始查看每个配置项，发现有这么一项：

::

    cfg.StrOpt('log-config-append',)

原来，以字符串形式定义配置项名称包括 ``-`` 时，由于它不是合法的名字标签字符，
会被当成负号。因此，cfg.py 库会对名称中的 ``-`` 替换成 ``_`` ,这样我们就可以
通过 CONF.log_config_append 获取该配置项值！

.. figure:: /_static/images/log_config_append.png
   :scale: 100
   :align: center

   搜索配置项


.. figure:: /_static/images/opt_replace.png
   :scale: 100
   :align: center

   oslo.config.cfg 模块替换配置项名称下划线

加载配置文件
+++++++++++++++++

**update: 2016/12/26-12-40**

这种方式，也是我在阅读 nova/openstack/common/log 模块代码时注意到的。
log 模块设置nova的日志保存在 /var/log/nova/ 目录下，该项由 /etc/nova/nova.conf
配置文件指定：

:file:`/etc/nova/nova.conf`

::

    logdir=/var/log/nova

我们知道，oslo.config 默认存在 --config-file 和 --config-dir 选项，后来我从命令行启动的方式，
根本不指定任务参数，可是 CONF.config_file 还是正确加载 /etc/nova/nova.conf 文件。来看看我的
测试方式：

:file:`cmd/scheduler.py`

::

    def main():
        #config.parse_args(sys.argv)
        CONF(project='nova')
        print "+++===+++ CONF.config_dir2:", CONF.config_dir
        print "+++===+++ CONF.config_file2:", CONF.config_file

利用  /usr/bin/nova-scheduler 不带任何参数，直接启动 nova-scheduler 还是可以正确加载配置文件，
为了分析出nova组件是如何正确加载 /etc/nova/nova.conf 文件，我折腾了一个上午(效率很低哈！)。

原来，在 nova/config.py 文件中，进行参数解析时指定了一个额外的参数 project，如此就可以找到
/etc/nova/nova.conf 配置文件了！

:file:`nova/config.py`

::

    CONF(argv[1:],
         project='nova',
         version=version.version_string(),
         default_config_files=default_config_files)


.. figure:: /_static/images/get_config_dir.png
   :scale: 100
   :align: center

   通过 project 参数查找配置文件目录

记录所有的配置项
+++++++++++++++++

**update: 2017-1-8 18:30**

该函数的用法也是在分析nova组件源码时学习到的，会尝试
以level级别记录CONF所有的配置项：

.. method:: ConfigOpts.log_opt_values(self, logger, level)

    :param logger: logging.Logger 对象
    :param level: 记录配置项的级别

比如，在 :file:`nova/openstack/common/service.py` 中，有这样一处代码：

::

    CONF.log_opt_values(LOG, std_logging.DEBUG)

这里尝试以DEBUG级别记录配置项。但是nova组件默认的日志级别为 ``INFO`` ， 因此
我们可以通过命令行开启 ``--debug`` 选项，然后所有的配置项都会输出到日志。


.. figure:: /_static/images/log_opt_values.png
   :scale: 100
   :align: center

   输出所有配置项值


变量引用和替换
+++++++++++++++

**update: 2017-1-10**

oslo.config 支持配置项引用其他配置项的值。

::

    cfg.StrOpt('state_path', default='/root')
    cfg.StrOpt('instances_path',
               default='$state_path/instances')

如上所示，instances_path直接引用state_path配置项作为默认值的一部分。

.. code-block:: console

    root@allinone-v2:/smbshare# ./test_cfg.py 
    instances_path: /root/instances
    state_path: /root

这种用法也是在分析源码时发现的。实际上，这种用法在openstack官网
文档有清晰的描述。看来还是得好好看文档！



---------------------

参考
=====

.. [#] https://blog.apporc.org/2016/08/python-%E9%85%8D%E7%BD%AE%E7%AE%A1%E7%90%86%EF%BC%9Aoslo-config/
.. [#] http://www.choudan.net/2013/11/28/OpenStack-Oslo.config-%E5%AD%A6%E4%B9%A0(%E4%BA%8C).html
.. [#] http://blog.xiayf.cn/2013/03/30/argparse/
.. [#] http://lingxiankong.github.io/blog/2014/08/31/openstack-oslo-config/
