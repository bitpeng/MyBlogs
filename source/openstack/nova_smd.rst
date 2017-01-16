.. _nova_SMD:

[翻译] nova：Services、Managers and Drivers
############################################

参考链接：http://docs.openstack.org/developer/nova/services.html


对于初次接触nova的新手来说，Services/Managers/Drivers的作用可能让人很困惑。该文档就试图概括他们之间的区别，使得理解系统更容易！


当前，Managers 和 Drivers 通过标志指定，并使用utils.load_object() 加载，该函数允许他们(指Managers和Drivers)通过单态、类、模块或者对象来实现。只要(通过标志指定的)路径指向一个(响应getattr的)对象(或者返回一个对象的callable)，它就应该是manager或dirver！

nova.service 模块
=================

所有运行在hosts工作进程的通用节点基类！

每个 service 对象都有一个或多个manager对象，manager 对象是 rpcserver 的 endpoints，并通过topic监听消息队列。service对象也可以运行 manager 对象的周期性任务并报告它的状态给数据库状态服务表。

Service 类定义如下：

::

    class Service(host, binary, topic, manager, report_interval=None, 
                  periodic_enable=None, periodic_fuzzy_delay=None, 
                  periodic_interval_max=None, *args, **kwargs):
                  
相关方法：

.. method:: Service.basic_config_check()

    服务运行前执行基本的检查；

.. classmethod:: Service.create(host=None, binary=None, topic=None, manager=None, report_interval=None, periodic_enable=None, periodic_fuzzy_delay=None, periodic_interval_max=None)

    :param host: defaults to CONF.host；
    :param binary: defaults to basename of executable;
    :param topic: 默认是 bin_name - 'nova-' (如： "nova-conductor" 减去 "nova-" 为 "conductor")
    :param manager: defaults to CONF.<topic>_manager
    :param report_interval: defaults to CONF.report_interval
    :param periodic_enable: defaults to CONF.periodic_enable
    :param periodic_fuzzy_delay: defaults to CONF.periodic_fuzzy_delay
    :param periodic_interval_max:  如果设置，周期性任务执行的最大间隔时间；

.. method:: Service.periodic_tasks(raise_on_error=False)

    周期性运行的任务。


nova.manager 模块
=================

Manager 基类。

Manager 负责系统的某个特定方面。它是关系系统某一部分的一组逻辑代码。一般来说，其他组件应该使用Managers对它负责的组件进行更改。

例如，其他组件需要以某种方式处理卷，那它应该使用 VolumeManager的方法，而不是直接更改数据库域。这允许我们把所有与卷相关的代码放在同一个地方！


我们采用了智能managers和哑数据的基本策略，这意味着不是把方法附加给数据对象，而是组件需要调用manager的(作用于数据的)方法


managers的方法能在本机运行的应该直接调用。如果某些特殊的方法需要在远程host上执行，这应该通过发送RPC调用给(包装了manager的)service。


Managers负责绝大部分的数据访问，但是不实现特定的数据。需要特定实现的任何东西(不能通用化的)都应该由Driver去做！


通常，我们倾向使用一个Manager对应不同的Drivers实现，但有时有很多Managers是必要的。你可以这样想：在manager层抽象不同的所有策略(如FlatNetwork和VlanNetwork)，在Drivers层做不同的实现(LinuxNetDriver 和 CiscoNetDriver)。


Managers 通常提供方法，用来进行主机初始化设置或者包装了服务的周期性任务初始化设置！


该模块提供 Manager， managers的基类。

::

    class Manager(host=None, db_driver=None, service_name='undefined')

相关方法：

.. method:: cleanup_host()

    当服务停止时，清理工作的钩子函数，子类应该重写该方法
    
.. method:: init_host()

    Hook to do additional manager initialization when one requests the service be started. This is called before any service record is created.
    
    子类也应该重写该类！
    
.. method:: periodic_tasks(context, raise_on_error=False)

    运行周期性任务

.. method:: post_start_hook()

    Hook to provide the manager the ability to do additional start-up work immediately after a service creates RPC consumers and starts ‘running’.

    Child classes should override this method.

.. method:: pre_start_hook()

    Hook to provide the manager the ability to do additional start-up work before any RPC
    queues/consumers are created. This is called after other initialization 
    has succeeded and a service record is created.
    
    Child classes should override this method.

.. method:: reset()

    Hook called on SIGHUP to signal the manager to re-read any dynamic
    configuration or do any reconfiguration tasks.
    
Drivers:特定实现
================

一个manager为它的任务加载driver。driver 负责特定实现细节。任何一个主机上运行shell命令，或处理其他非Python代码都应该在一个driver发生。

Drivers应该尽可能少的操作数据库，尽管当前允许实现操作特定数据。这可能在以后会重新考虑！

通常为特定的driver定义一个抽象基类是必要的，并在抽象基类中定义不同driver需要实现的方法。

.. [#] http://www.aboutyun.com/thread-9264-1-1.html


