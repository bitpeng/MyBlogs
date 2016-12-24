.. _oslo_cfg:


########################
oslo.config 库学习
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. contents:: 目录

--------------------------

分析OpenStack源码过程中，它使用了很多很多的库，假如不了解这些库的用法，
代码会非常难以理解。oslo作为OpenStack的通用组件，在每一个项目中都有
用到，现在对子项目 ``oslo.config`` 用法做一个总结！由于 oslo.config 
支持的功能非常的多，因此这里可能只会列出常用的用法。

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

::

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

::

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

::

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

::

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

---------------------

参考
=====

.. [#] https://blog.apporc.org/2016/08/python-%E9%85%8D%E7%BD%AE%E7%AE%A1%E7%90%86%EF%BC%9Aoslo-config/
.. [#] http://www.choudan.net/2013/11/28/OpenStack-Oslo.config-%E5%AD%A6%E4%B9%A0(%E4%BA%8C).html
.. [#] http://blog.xiayf.cn/2013/03/30/argparse/
.. [#] http://lingxiankong.github.io/blog/2014/08/31/openstack-oslo-config/
