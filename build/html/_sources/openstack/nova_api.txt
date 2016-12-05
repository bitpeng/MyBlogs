.. _nova-api:

nova-api分析
#############

下面从 ``nova --debug list`` 着手分析 ``nova-api`` 的处理流程！

::

    root@juno-controller:/smbshare/paste_test# nova --debug list
    REQ: curl -i 'http://100.100.100.254:5000/v2.0/tokens' -X POST -H "Accept: application/json" -H "Content-Type: application/json" -H "User-Agent: python-novaclient" -d '{"auth": {"tenantName": "csq", "passwordCredentials": {"username": "chensq", "password": "{SHA1}c60f964054e2080b1c827fae07ef0e5d92d2d285"}}}'
    …………

    REQ: curl -i 'http://100.100.100.254:8774/v2/a0e0c1b46fe94e1c90bd15e358d39486/servers/detail' -X GET -H "Accept: application/json" -H "User-Agent: python-novaclient" -H "X-Auth-Project-Id: csq" -H "X-Auth-Token: {SHA1}69c17566ddec8dc5488593dd36e6484c82242d71"
    …………

可以看到，获取租户虚机列表命令 ``nova --debug list`` 先要向 ``keystone`` 发起请求，获取用户token。这一步分析省略！

然后获取token后，然后利用该token，向 ``nova-api`` 发起请求，获取虚机列表。

首先，我们需要定位到该url: ``v2/a0e0c1b46fe94e1c90bd15e358d39486/servers/detail`` 对应的处理程序。

.. code-block:: shell

    # vi /etc/nova/api-paste.ini
    [composite:osapi_compute]
    use = call:nova.api.openstack.urlmap:urlmap_factory
    /: oscomputeversions
    /v1.1: openstack_compute_api_v2
    /v2: openstack_compute_api_v2
    /v2.1: openstack_compute_api_v21
    /v3: openstack_compute_api_v3

    [composite:openstack_compute_api_v2]
    use = call:nova.api.auth:pipeline_factory
    noauth = compute_req_id faultwrap sizelimit noauth ratelimit osapi_compute_app_v2
    keystone = compute_req_id faultwrap sizelimit authtoken keystonecontext ratelimit osapi_compute_app_v2
    keystone_nolimit = compute_req_id faultwrap sizelimit authtoken keystonecontext osapi_compute_app_v2

    [app:osapi_compute_app_v2]
    paste.app_factory = nova.api.openstack.compute:APIRouter.factory

这里只选取了 ``api-paste.ini`` 文件的部分配置项！可以看到，
URL以/v2开头的请求，最终由 ``osapi_compute_app_v2`` 处理！

``/nova/api/openstack/compute/__init__.py`` 中定义的 :class:`APIRouter` 作为
``os_api_compute_app_v2`` 的入口!

继承体系：

:class:`nova.api.openstack.compute:APIRouter` --> :class:`nova.api.openstack.APIRouter`

:class:`nova.api.openstack.APIRouter` 定义了 :meth:`factory` 类方法：

::

    class APIRouter(base_wsgi.Router):
        """Routes requests on the OpenStack API to the appropriate controller
        and method.
        """
        ExtensionManager = None  # override in subclasses

        @classmethod
        def factory(cls, global_config, **local_config):
            """Simple paste factory, :class:`nova.wsgi.Router` doesn't have one."""
            return cls()

该方法返回的app对象作为以/v2开头的http请求的入口：即当有req请求到来，并且req.path 以/v2开头，
``paste.deploy`` 包装会把该请求转发给 :class:`APIRouter` 对象处理，因此会调用 :meth:`APIRouter.__call__` 函数！

::

    class Router(object):
        """WSGI middleware that maps incoming requests to WSGI apps."""

        def __init__(self, mapper):
            """Create a router for the given routes.Mapper.

            Each route in `mapper` must specify a 'controller', which is a
            WSGI app to call.  You'll probably want to specify an 'action' as
            well and have your controller be an object that can route
            the request to the action-specific method.

            Examples:
              mapper = routes.Mapper()
              sc = ServerController()

              # Explicit mapping of one route to a controller+action
              mapper.connect(None, '/svrlist', controller=sc, action='list')

              # Actions are all implicitly defined
              mapper.resource('server', 'servers', controller=sc)

              # Pointing to an arbitrary WSGI app.  You can specify the
              # {path_info:.*} parameter so the target app can be handed just that
              # section of the URL.
              mapper.connect(None, '/v1.0/{path_info:.*}', controller=BlogApp())

            """
            self.map = mapper
            self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                              self.map)

        @webob.dec.wsgify(RequestClass=Request)
        def __call__(self, req):
            """Route the incoming request to a controller based on self.map.

            If no match, return a 404.

            """
            return self._router

        @staticmethod
        @webob.dec.wsgify(RequestClass=Request)
        def _dispatch(req):
            """Dispatch the request to the appropriate controller.

            Called by self._router after matching the incoming request to a route
            and putting the information into req.environ.  Either returns 404
            or the routed WSGI app's response.

            """
            match = req.environ['wsgiorg.routing_args'][1]
            if not match:
                return webob.exc.HTTPNotFound()
            app = match['controller']
            return app


这一步的处理流程是：:meth:`APIRouter.__call__` --> :meth:`APIRouter._dispatch` ，
由于这两个函数返回的都是 ``wsgi app`` 对象，因此会继续调用该对象。
最后 :meth:`APIRouter._dispatch()` 返回app, 实际上该app的值是在 :meth:`mapper.connect` 或者
:meth:`mapper.resource` 时定义的 ``controller`` 实参对象！

::

    # /nova/api/openstack/compute/__init__.py
    class APIRouter(nova.api.openstack.APIRouter):
        """Routes requests on the OpenStack API to the appropriate controller
        and method.
        """
        ExtensionManager = extensions.ExtensionManager

        def _setup_routes(self, mapper, ext_mgr, init_only):
            if init_only is None or 'versions' in init_only:
                self.resources['versions'] = versions.create_resource()
                mapper.connect("versions", "/",
                            controller=self.resources['versions'],
                            action='show',
                            conditions={"method": ['GET']})

            mapper.redirect("", "/")

            if init_only is None or 'consoles' in init_only:
                self.resources['consoles'] = consoles.create_resource()
                mapper.resource("console", "consoles",
                            controller=self.resources['consoles'],
                            parent_resource=dict(member_name='server',
                            collection_name='servers'))

            if init_only is None or 'consoles' in init_only or \
                    'servers' in init_only or 'ips' in init_only:
                self.resources['servers'] = servers.create_resource(ext_mgr)
                mapper.resource("server", "servers",
                                controller=self.resources['servers'],
                                collection={'detail': 'GET'},
                                member={'action': 'POST'})

根据这里可以看到，:meth:`Router._dispatch` 返回的app实际上是
:class:`/nova/api/openstack/wsgi:Resource` 对象， 因此会继续调用它的 :meth:`__call__` 方法，
实际上，我们根据 :func:`mapper.resource` 的 ``controller`` 参数可以知道。最终会调用
:meth:`/nova/api/openstack/compute/servers:Controller.detail` 方法！然后可以进入该方法，进行具体分析。
由于我这里只分析 ``nova-api`` 的处理流程，因此代码细节分析略！
