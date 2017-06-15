.. _pecan_note:


########################
pecan学习示例
########################


.. contents:: 目录

--------------------------


在openstack的某些项目如ceilometer中，摒弃了paste+webob这种复杂的构建rest-API的方式，
才是采用了全新的框架：pecan。在网上搜索学习了下，入门确实比paste+webob简单很多，
现在通过例子来熟悉下。参考网址：http://www.giantflyingsaucer.com/blog/?p=4834


入门示例
+++++++++

首先通过下面的命令，新建一个pecan项目：

::

    mkdir pecanrest-proj
    cd pecanrest-proj

    pip install pecan
    pecan create pecanrest
    cd pecanrest
    python setup.py develop

由于新建的pecan项目默认监听端口为8080，和ceph-inkscope监听端口冲突，
因此编辑config.py文件，设置监听端口为18080。

启动pecan项目并测试：

::

    pecan serve config.py


.. figure:: /_static/images/pecan_test.png
   :scale: 100
   :align: center

然后尝试给项目加上版本信息，编辑root.py文件，加上如下代码：

::

    from pecanrest.controllers import v1

    class RootController(object):

        v1 = v1.VersionController()


然后在root.py文件所在目录新建v1.py，代码如下：

::

    #v1.py
    import pecan
    from pecan import rest

    class VersionController(rest.RestController):
        @pecan.expose('json')
        def get(self):
            return {"api version": "1.0"}

重新启动服务，并测试。

.. code-block:: console

    root@ubuntu:/smbshare# curl http://192.168.159.155:18080/v1
    {"api version": "1.0"}


下一步测试，在controller目录下新建api目录，并包含三个文件：__init__.py，api.py，order.py。

其中每一个文件内容如下：

::

    # api.py
    from pecanrest.controllers.api import order
    import pecan

    class ApiController(object):
        orders = order.OrdersController()
        testhh = order.OrdersController()

        @pecan.expose('json')
        def index(self):
            return {"version": "1.0.0", "info": "test api"}

::

    # order.py
    import pecan
    from pecan import rest, response

    class OrdersController(rest.RestController):

        @pecan.expose("json")
        def get(self):
            return {
                "100A": "1 bag of corn",
                "293F": "2 bags of potatoes",
                "207B": "1 bag of carrots"
            }

        @pecan.expose()
        def post(self):
            # TODO: Create a new order, (optional) return some status data
            response.status = 201
            return "POST SUCCESS!\n"

        @pecan.expose()
        def put(self):
            # TODO: Idempotent PUT (return 200 or 204)
            #response.status = 204
            response.status = 205
            return "PUT SUCCESS!\n"

        @pecan.expose()
        def delete(self):
            # TODO: Idempotent DELETE
            response.status = 200
            return "DELETE SUCCESS\n"


然后编辑root.py加上下面的内容：

::

    from pecanrest.controllers import v1
    from pecanrest.controllers.api import api

    class RootController(object):

        v1 = v1.VersionController()
        api = api.ApiController()


重新启动服务并测试：

.. code-block:: console

    root@ubuntu:/smbshare# 
    root@ubuntu:/smbshare# curl http://192.168.159.155:18080/api/orders
    {"293F": "2 bags of potatoes", "207B": "1 bag of carrots", "100A": "1 bag of corn"}root@ubuntu:/smbshare# 
    root@ubuntu:/smbshare# 
    root@ubuntu:/smbshare# curl http://192.168.159.155:18080/api/testhh
    {"293F": "2 bags of potatoes", "207B": "1 bag of carrots", "100A": "1 bag of corn"}root@ubuntu:/smbshare# 
    root@ubuntu:/smbshare# 
    root@ubuntu:/smbshare# curl -X POST http://192.168.159.155:18080/api/testhh
    POST SUCCESS!
    root@ubuntu:/smbshare# 
    root@ubuntu:/smbshare# curl -X PUT http://192.168.159.155:18080/api/testhh
    PUT SUCCESS!
    root@ubuntu:/smbshare# 
    root@ubuntu:/smbshare# curl -X DELETE http://192.168.159.155:18080/api/testhh
    DELETE SUCCESS


把这个例子动手操作一篇，pecan就会有一个大概的了解了。

附上项目controller目录结构：

.. code-block:: console

    root@allinone-v2:/smbshare/pecanrest-proj/pecanrest/pecanrest# tree controllers/
    controllers/
    ├── api
    │   ├── api.py
    │   ├── api.pyc
    │   ├── __init__.py
    │   ├── __init__.pyc
    │   ├── order.py
    │   └── order.pyc
    ├── __init__.py
    ├── __init__.pyc
    ├── root.py
    ├── root.pyc
    ├── v1.py
    └── v1.pyc


url查询字符串
++++++++++++++

后来在ceilometer的扩展开发中，需要在http请求中加上URL查询字符串，这里可以用下面的实现方法。

.. figure:: /_static/images/query_string.png
   :scale: 100
   :align: center

.. figure:: /_static/images/test_pecan_query_string.png
   :scale: 100
   :align: center


---------------------

参考
+++++

.. [#] http://www.giantflyingsaucer.com/blog/?p=4834
