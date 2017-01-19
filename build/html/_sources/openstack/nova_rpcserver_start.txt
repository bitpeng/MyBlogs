.. _nova_rpcserver:


############################
nova rpc服务启动分析
############################


.. contents:: 目录

--------------------------

最近一直在分析 nova 项目源码，渐有心得，因此萌生了自己也写些nova 源码分析的
博文。在网上已有nova源码分析的很多文章，自己当初也参考了很多，在此表示感谢。
最后还是决定自己动手写一些，以加深理解，并作总结！

.. note::

    nova项目重度依赖于 oslo.messaging 和 oslo.config, 前者是OpenStack
    通用消息库，后者是OpenStack通用配置文件和命令行处理库。假如对两个库
    的相关概念和用法不熟悉，那么阅读代码会非常困难，尤其是消息队列。因此
    建议事先熟悉下这两个库，也可以参考笔者之前写的一些文章！
    如：:ref:`rabbitmq教程 <rabbitmq_doc>` , :ref:`oslo.config库学习 <oslo_cfg>` 和
    :ref:`kombu和消息队列 <kombu>`

    另外，由于模块多，组件间调用关系复杂，推荐使用 ``OpenGrok`` 来浏览代码！

    **代码基于 juno 版本，部署于 ubuntu-14.04 LTS**

服务创建
=========

我们以 nova-conductor 为例，说明 nova rpcserver 是如何启动的。

每一个 nova-service 实际上都是运行在 host 上的程序，我们可以通过 ``ps -ef | grep nova`` 
来查看相关进程信息：

::

    root@allinone-v2:/opt/cecgw/csmp/nova# ps -ef | grep nova
    root     27508 39229  1 Dec21 pts/10   00:17:04 /usr/bin/python /usr/bin/nova-conductor --debug --config-file=/etc/nova/nova.conf
    root     27514 27508  0 Dec21 pts/10   00:05:34 /usr/bin/python /usr/bin/nova-conductor --debug --config-file=/etc/nova/nova.conf
    root     27515 27508  0 Dec21 pts/10   00:05:30 /usr/bin/python /usr/bin/nova-conductor --debug --config-file=/etc/nova/nova.conf
    root     27728 39229  1 Dec21 pts/10   00:16:33 /usr/bin/python /usr/bin/nova-api --debug --config-file=/etc/nova/nova.conf
    root     27736 27728  0 Dec21 pts/10   00:00:00 /usr/bin/python /usr/bin/nova-api --debug --config-file=/etc/nova/nova.conf
    ......
    
然后查看 /usr/bin/nova-conductor 文件，它实际上是调用 nova/cmd/conductor.py !

:file:`nova/cmd/conductor.py`

::

    # 从其他模块导入conductor topic
    CONF = cfg.CONF
    CONF.import_opt('topic', 'nova.conductor.api', group='conductor')


    def main():
        # 服务启动，命令行参数解析，并设置 exchange、初始化全局 transport
        config.parse_args(sys.argv)
        # 日志设施
        logging.setup("nova")
        # 使用eventlet 作为 线程模型，需要绿化！
        utils.monkey_patch()
        objects.register_all()

        gmr.TextGuruMeditation.setup_autorun(version)

        # 生成服务对象
        server = service.Service.create(binary='nova-conductor',
                                        topic=CONF.conductor.topic,
                                        manager=CONF.conductor.manager)
        workers = CONF.conductor.workers or processutils.get_worker_count()
        service.serve(server, workers=workers)
        service.wait()

:file:`nova/conductor/api.py`

::

    conductor_opts = [
        cfg.BoolOpt('use_local',
                    default=False,
                    help='Perform nova-conductor operations locally'),
        cfg.StrOpt('topic',
                   default='conductor',
                   help='The topic on which conductor nodes listen'),
        cfg.StrOpt('manager',
                   default='nova.conductor.manager.ConductorManager',
                   help='Full class name for the Manager for conductor'),
        cfg.IntOpt('workers',
                   help='Number of workers for OpenStack Conductor service. '
                        'The default will be the number of CPUs available.')
    ]
    conductor_group = cfg.OptGroup(name='conductor',
                                   title='Conductor Options')
    CONF = cfg.CONF
    CONF.register_group(conductor_group)
    CONF.register_opts(conductor_opts, conductor_group)

我们来看这里服务创建的关键 Service.create 方法：


:file:`nova/service.py`
::

    class Service(service.Service):
        """Service object for binaries running on hosts.

        A service takes a manager and enables rpc by listening to queues based
        on topic. It also periodically runs tasks on the manager and reports
        it state to the database services table.
        """
        def __init__(self, host, binary, topic, manager, report_interval=None,
                     periodic_enable=None, periodic_fuzzy_delay=None,
                     periodic_interval_max=None, db_allowed=True,
                     *args, **kwargs):
            super(Service, self).__init__()
            self.host = host
            self.binary = binary
            self.topic = topic
            self.manager_class_name = manager
            # NOTE(russellb) We want to make sure to create the servicegroup API
            # instance early, before creating other things such as the manager,
            # that will also create a servicegroup API instance.  Internally, the
            # servicegroup only allocates a single instance of the driver API and
            # we want to make sure that our value of db_allowed is there when it
            # gets created.  For that to happen, this has to be the first instance
            # of the servicegroup API.
            self.servicegroup_api = servicegroup.API(db_allowed=db_allowed)
            manager_class = importutils.import_class(self.manager_class_name)
            self.manager = manager_class(host=self.host, *args, **kwargs)
            self.rpcserver = None
            self.report_interval = report_interval
            self.periodic_enable = periodic_enable
            self.periodic_fuzzy_delay = periodic_fuzzy_delay
            self.periodic_interval_max = periodic_interval_max
            self.saved_args, self.saved_kwargs = args, kwargs
            self.backdoor_port = None
            self.conductor_api = conductor.API(use_local=db_allowed)
            self.conductor_api.wait_until_ready(context.get_admin_context())

        @classmethod
        def create(cls, host=None, binary=None, topic=None, manager=None,
                   report_interval=None, periodic_enable=None,
                   periodic_fuzzy_delay=None, periodic_interval_max=None,
                   db_allowed=True):
            """Instantiates class and passes back application object.

            :param host: defaults to CONF.host
            :param binary: defaults to basename of executable
            :param topic: defaults to bin_name - 'nova-' part
            :param manager: defaults to CONF.<topic>_manager
            :param report_interval: defaults to CONF.report_interval
            :param periodic_enable: defaults to CONF.periodic_enable
            :param periodic_fuzzy_delay: defaults to CONF.periodic_fuzzy_delay
            :param periodic_interval_max: if set, the max time to wait between runs

            """
            if not host:
                host = CONF.host
            if not binary:
                binary = os.path.basename(sys.argv[0])
            if not topic:
                topic = binary.rpartition('nova-')[2]
            if not manager:
                manager_cls = ('%s_manager' %
                               binary.rpartition('nova-')[2])
                manager = CONF.get(manager_cls, None)
            if report_interval is None:
                report_interval = CONF.report_interval
            if periodic_enable is None:
                periodic_enable = CONF.periodic_enable
            if periodic_fuzzy_delay is None:
                periodic_fuzzy_delay = CONF.periodic_fuzzy_delay

            debugger.init()

            service_obj = cls(host, binary, topic, manager,
                              report_interval=report_interval,
                              periodic_enable=periodic_enable,
                              periodic_fuzzy_delay=periodic_fuzzy_delay,
                              periodic_interval_max=periodic_interval_max,
                              db_allowed=db_allowed)

            return service_obj

create 方法是根据 topic, binary, manager 参数，生成 Service 实例对象！

__init__ 方法中有两个地方需要注意：

一是根据 manager_name 动态导入 manager 类。每一个 service 都用 manager 对象干
一些特定的工作！通过 importutils.import_class 实现。

:file:`nova/openstack/common/importutils.py`

::

    # 根据字符串，动态导入类，并返回！
    def import_class(import_str):
        """Returns a class from a string including module and class."""
        mod_str, _sep, class_str = import_str.rpartition('.')
        __import__(mod_str)
        try:
            return getattr(sys.modules[mod_str], class_str)
        except AttributeError:
            raise ImportError('Class %s cannot be found (%s)' %
                              (class_str,
                               traceback.format_exception(*sys.exc_info())))

二是 ``self.conductor_api.wait_until_ready(context.get_admin_context())``，
这处代码的功能是：根据 db_allowed 的值，确定组件是否被允许直接访问数据库。
假如允许，函数直接返回；假如不允许直接访问数据库，那么一直等待，等到 nova-conductor
服务启动。

浏览其他组件代码如: nova-schedule, nova-compute，可以看到， nova-conductor/nova-schedule
允许直接访问数据库，而 nova-compute 不能直接访问。

我们可以关闭 nova-conductor，然后重启 nova-compute ，看看是什么结果！

.. figure:: /_static/images/wait_nova_conductor.png
   :scale: 100
   :align: center

   提示告警信息，nova-conductor 服务没有启动！

我们可以看看这里是如何实现的：

:file:`nova/conductor/__init__.py`

::

    def API(*args, **kwargs):
        use_local = kwargs.pop('use_local', False)
        if oslo.config.cfg.CONF.conductor.use_local or use_local:
            api = conductor_api.LocalAPI
        else:
            api = conductor_api.API
        return api(*args, **kwargs)

API 函数依据是否允许直接访问数据库，返回 nova.conductor.api.API 或者
nova.conductor.api.LocalAPI 对象！

::

    class LocalAPI(object):
        """A local version of the conductor API that does database updates
        locally instead of via RPC.
        """

        def __init__(self):
            # TODO(danms): This needs to be something more generic for
            # other/future users of this sort of functionality.
            self._manager = utils.ExceptionHelper(manager.ConductorManager())

        def wait_until_ready(self, context, *args, **kwargs):
            # nothing to wait for in the local case.
            pass

    class API(LocalAPI):
        """Conductor API that does updates via RPC to the ConductorManager."""

        def __init__(self):
            self._manager = rpcapi.ConductorAPI()
            self.base_rpcapi = baserpc.BaseAPI(topic=CONF.conductor.topic)

        def wait_until_ready(self, context, early_timeout=10, early_attempts=10):
            '''Wait until a conductor service is up and running.

            This method calls the remote ping() method on the conductor topic until
            it gets a response.  It starts with a shorter timeout in the loop
            (early_timeout) up to early_attempts number of tries.  It then drops
            back to the globally configured timeout for rpc calls for each retry.
            '''
            attempt = 0
            timeout = early_timeout
            # if we show the timeout message, make sure we show a similar
            # message saying that everything is now working to avoid
            # confusion
            has_timedout = False
            while True:
                # NOTE(danms): Try ten times with a short timeout, and then punt
                # to the configured RPC timeout after that
                if attempt == early_attempts:
                    timeout = None
                attempt += 1

                # NOTE(russellb): This is running during service startup. If we
                # allow an exception to be raised, the service will shut down.
                # This may fail the first time around if nova-conductor wasn't
                # running when this service started.
                try:
                    self.base_rpcapi.ping(context, '1.21 GigaWatts',
                                          timeout=timeout)
                    if has_timedout:
                        LOG.info(_('nova-conductor connection '
                                   'established successfully'))
                    break
                except messaging.MessagingTimeout:
                    has_timedout = True
                    LOG.warning(_('Timed out waiting for nova-conductor.  '
                                  'Is it running? Or did this service start '
                                  'before nova-conductor?  '
                                  'Reattempting establishment of '
                                  'nova-conductor connection...'))

LocalAPI 的 wait_until_ready 方法直接返回，所以不需要等待 nova-conductor 服务启动。
而 API.wait_until_ready() 方法会发起 RPC 调用并阻塞等待结果！
self.base_rpcapi对象 topic 值为 "conductor" , 利用call() 方法发送消息时，
只有 topic 值也是 "conductor" ，并且 version 不低于 "1.0" 的 rpcserver 才会处理！

后面分析服务启动的start方法时，能看到，每一个rpcserver 服务的 endpoints 都
包括 ``BaseRPCAPI`` 对象！nova-conductor 服务的 BaseRPCAPI 实例化对象 topic 值刚好是 "conductor"，
我们可以从代码中看到这一点。所以，只有 nova-conductor 服务启动了，并
处理 base_rpcapi 发起的 call 请求，才会退出 while 循环！

:file:`nova/conductor/manager.py`
::

    class ConductorManager(manager.Manager):
        """Mission: Conduct things.

        The methods in the base API for nova-conductor are various proxy operations
        performed on behalf of the nova-compute service running on compute nodes.
        Compute nodes are not allowed to directly access the database, so this set
        of methods allows them to get specific work done without locally accessing
        the database.

        The nova-conductor service also exposes an API in the 'compute_task'
        namespace.  See the ComputeTaskManager class for details.
        """

        target = messaging.Target(version='2.0')

        def __init__(self, *args, **kwargs):
            super(ConductorManager, self).__init__(service_name='conductor',
                                                   *args, **kwargs)
 

ConductorManager 实例化设置 service_name， BaseRPCAPI实例化时会根据 service_name 设置 topic！
然后组成 endpoints 创建 rpcserver！

:file:`nova/service.py`
::
        
    class Service(service.Service):
        ......
        def start(self):
            ......
            endpoints = [
                self.manager,
                # 以service_name 作为 topic，BaseRPCAPI
                baserpc.BaseRPCAPI(self.manager.service_name, self.backdoor_port)
            ]
            ......
            self.rpcserver = rpc.get_server(target, endpoints, serializer)

:file:`nova/baserpc.py`
::

    class BaseAPI(object):
        """Client side of the base rpc API.

        API version history:

            1.0 - Initial version.
            1.1 - Add get_backdoor_port
        """

        VERSION_ALIASES = {
            # baseapi was added in havana
        }

        def __init__(self, topic):
            super(BaseAPI, self).__init__()
            target = messaging.Target(topic=topic,
                                      namespace=_NAMESPACE,
                                      version='1.0')
            version_cap = self.VERSION_ALIASES.get(CONF.upgrade_levels.baseapi,
                                                   CONF.upgrade_levels.baseapi)
            self.client = rpc.get_client(target, version_cap=version_cap)

        def ping(self, context, arg, timeout=None):
            arg_p = jsonutils.to_primitive(arg)
            cctxt = self.client.prepare(timeout=timeout)
            return cctxt.call(context, 'ping', arg=arg_p)

        def get_backdoor_port(self, context, host):
            cctxt = self.client.prepare(server=host, version='1.1')
            return cctxt.call(context, 'get_backdoor_port')


    class BaseRPCAPI(object):
        """Server side of the base RPC API."""

        target = messaging.Target(namespace=_NAMESPACE, version='1.1')

        def __init__(self, service_name, backdoor_port):
            self.service_name = service_name
            self.backdoor_port = backdoor_port

        def ping(self, context, arg):
            resp = {'service': self.service_name, 'arg': arg}
            return jsonutils.to_primitive(resp)

        def get_backdoor_port(self, context):
            return self.backdoor_port

启动服务
=========

经过上面这么多步骤，还只是创建了一个服务对象，服务并没有运行。我们接下来看下面的代码

::

    workers = CONF.conductor.workers or processutils.get_worker_count()
    service.serve(server, workers=workers)
    service.wait()

这里，会根据工作进程的数量，启动数目的进程(workers > 1) 或者启动一个绿色线程！
最后会调用之前生成的服务对象的 start 方法。

::

    def launch(service, workers=1):
        if workers is None or workers == 1:
            launcher = ServiceLauncher()
            launcher.launch_service(service)
        else:
            launcher = ProcessLauncher()
            launcher.launch_service(service, workers=workers)

        return launcher

在 Service.start 方法中，主要是创建真正的 rpcserver 服务，处理 manager_class 的周期性任务！
之前提到，每一个 rpcserver 都包括 BaseRPCAPI endpoint, 实际上，他们包括以下三类 endpoints:

- BaseRPCAPI
- CONF 配置中的 "%s_manager"%service_name，可以称之为主 manager
- 主 manager 对象初始化时生成的 additional_endpoints;

::

    def start(self):
        verstr = version.version_string_with_package()
        LOG.audit(_('Starting %(topic)s node (version %(version)s)'),
                  {'topic': self.topic, 'version': verstr})
        self.basic_config_check()
        self.manager.init_host()
        self.model_disconnected = False
        ctxt = context.get_admin_context()
        try:
            self.service_ref = self.conductor_api.service_get_by_args(ctxt,
                    self.host, self.binary)
            self.service_id = self.service_ref['id']
        except exception.NotFound:
            try:
                self.service_ref = self._create_service_ref(ctxt)
            except (exception.ServiceTopicExists,
                    exception.ServiceBinaryExists):
                # NOTE(danms): If we race to create a record with a sibling
                # worker, don't fail here.
                self.service_ref = self.conductor_api.service_get_by_args(ctxt,
                    self.host, self.binary)

        self.manager.pre_start_hook()

        if self.backdoor_port is not None:
            self.manager.backdoor_port = self.backdoor_port

        LOG.debug("Creating RPC server for service %s", self.topic)

        target = messaging.Target(topic=self.topic, server=self.host)

        endpoints = [
            self.manager,
            baserpc.BaseRPCAPI(self.manager.service_name, self.backdoor_port)
        ]
        endpoints.extend(self.manager.additional_endpoints)

        serializer = objects_base.NovaObjectSerializer()

        self.rpcserver = rpc.get_server(target, endpoints, serializer)
        self.rpcserver.start()

        self.manager.post_start_hook()

        LOG.debug("Join ServiceGroup membership for this service %s",
                  self.topic)
        # Add service to the ServiceGroup membership group.
        self.servicegroup_api.join(self.host, self.topic, self)

        if self.periodic_enable:
            if self.periodic_fuzzy_delay:
                initial_delay = random.randint(0, self.periodic_fuzzy_delay)
            else:
                initial_delay = None

            self.tg.add_dynamic_timer(self.periodic_tasks,
                                     initial_delay=initial_delay,
                                     periodic_interval_max=
                                        self.periodic_interval_max)


以 nova-conductor 为例，nova.Service 对象加载 ConductorManager，然后 ConductorManager
实例化时会加载 ComputeTaskManager, 最后这两者和 BaseRPCAPI 一起成为 nova-conductor RPCServer
的endpoints。

:file:`nova/conductor/manager.py`
::

    class ConductorManager(manager.Manager):
        target = messaging.Target(version='2.0')

        def __init__(self, *args, **kwargs):
            super(ConductorManager, self).__init__(service_name='conductor',
                                                   *args, **kwargs)
            self.security_group_api = (
                openstack_driver.get_openstack_security_group_driver())
            self._network_api = None
            self._compute_api = None
            self.compute_task_mgr = ComputeTaskManager()
            self.cells_rpcapi = cells_rpcapi.CellsAPI()
            self.additional_endpoints.append(self.compute_task_mgr)

nova 所有的rpcserver组件都遵循 service-manager-drivers 架构。nova.Service 创建服务对象，
然后加载 对应的 manager_class 如: nova.conductor.manager.ConductorManager, 最后由在
drivers 中实现代码细节。感觉这种架构很强大！具体可以参考：:ref:`nova service manager driver <nova_smd>`

