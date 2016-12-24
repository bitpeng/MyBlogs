.. _paste_webob_routes:


#############################################
OpenStack REST-API基础：paste/webob/routes库
#############################################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::

    在OpenStack 组件中，每一类组件服务入口都是通过rest-API提供的。而python rest-api服务的发布涉及
    到wsgi，路由分发等诸多问题。openstack使用的paste+webob+routes模块，使用起来比较复杂，自己因此也
    花费了很多时间也学习相关基础知识，渐有心得，因此记录下来，供参考。

.. contents:: 目录

--------------------------

paste库
========

程序示例
+++++++++

paste的核心是paste配置文件，因此看懂paste.ini配置文件是关键，先来看一个例子。

paste配置文件：

.. literalinclude:: /_static/src/pastedeploylab.ini
    :linenos:
    
使用paste.ini生成服务端程序：

.. literalinclude:: /_static/src/pastedeploylab.py
    :linenos:

运行服务端程序：

.. figure:: /_static/images/run_paste_test.png
   :scale: 100
   :align: center

   运行程序：服务端
   

.. figure:: /_static/images/curl_paste.png
   :scale: 100
   :align: center

   curl客户端测试
   
paste配置讲解
+++++++++++++

使用Paste和PasteDeploy模块来实现WSGI服务时，都需要一个paste.ini文件。
这个文件也是Paste框架的精髓，这里需要重点说明一下这个文件如何阅读。

paste.ini文件的格式类似于INI格式，每个section的格式为[type:name]。
这里重要的是理解几种不同type的section的作用。

.. attribute:: composite

    这种section用于将HTTP请求分发到指定的app。

.. attribute:: app

    这种section表示具体的app。

.. attribute:: filter

    实现一个过滤器中间件。关于wsgi中间件的知识可以参考 :ref:`wsgi 基础<wsgi_basic>`

.. attribute:: pipeline

    用来把把一系列的filter串起来。

然后对照程序，来挨个分析每个section。

section composite
-----------------

这种section用来决定如何分发HTTP请求。路由的对象其实就是paste.ini中其他secion的名字，类型必须是app或者pipeline。

::

    [composite:pdl]
    use=egg:Paste#urlmap        # use 为关键字
    /:root                      # "/" 开头的请求路由给root(对应pipeline:root)处理
    /calc:calc                  # "/calc" 开头的请求路由给calc处理
    #/v1:api_v1

    #[app:api_v1]
    #paste.app_factory = v1.router:MyRouterApp.factory

section pipeline
----------------

pipeline是把filter和app串起来的一种section。它只有一个关键字就是pipeline。

::

    [pipeline:root]
    pipeline = logrequest showversion

    [pipeline:calc]
    pipeline = test_filter calculator

pipeline指定的section有如下要求：

-   最后一个名字对应的section一定要是一个app；
-   除最后一个名字外其他名字对应的section一定要是一个filter；

pipeline关键字指定了很多个名字，这些名字也是paste.ini文件中其他section的名字。
请求会从最前面的section开始处理，一直向后传递。

.. figure:: /_static/images/call_filter_first.png
   :scale: 100
   :align: center

   filter定义在前，因此先调用filter,再调用app


section filter
---------------

filter是用来过滤请求和响应的，以WSGI中间件的方式实现。
其中的paste.filter_factory表示调用哪个函数来获得这个filter中间件。

::

    [filter:logrequest]
    username = root
    password = root123
    paste.filter_factory = pastedeploylab:LogFilter.factory
    # 调用pastedeploylab 的LogFilter 类的factory函数获得 logrequest中间件！
    # username 和 password是定义的变量。
    

    # add by chenshiqiang for test
    [filter:test_filter]
    k1 = m1
    k2 = m2
    paste.filter_factory = pastedeploylab:TestFilter.factory
    # 调用pastedeploylab 的TestFilter 的factory 函数获取 test_filter中间件！
    # end add

section app
-----------

app表示实现主要功能的应用，是一个标准的WSGI application。
paste.app_factory表示调用哪个函数来获得这个app。

::

    [app:showversion]
    version = 1.0.0
    paste.app_factory = pastedeploylab:ShowVersion.factory

    [app:calculator]
    description = This is an "+-*/" Calculator
    paste.app_factory = pastedeploylab:Calculator.factory


loadapp() name参数
++++++++++++++++++

loadapp 函数的name很关键，必须和配置文件的某个 composite对应上，否则出错。
实际上，name变量表示paste.ini中一个section的名字，指定这个section作为HTTP请求处理的第一站。

::

    #wsgi_app = loadapp("config:%s" % os.path.abspath(configfile), appname)
    wsgi_app = loadapp("config:%s" % os.path.abspath(configfile), "test_paste")

.. figure:: /_static/images/modify_app_name_error.png
   :scale: 100
   :align: center

   更改name 参数程序报错

   
URL匹配
++++++++

路径不是绝对匹配，只要开头匹配就可以，但是假如有更精确的匹配，那就采用更精确的。(有点类似于IP路由的最长最佳路由匹配)

.. figure:: /_static/images/paste_head_match.png
   :scale: 100
   :align: center

   开头匹配和最长精确匹配

总结
+++++

paste.ini中这一大堆配置的作用就是把我们用Python写的WSGI application和middleware串起来，规定好HTTP请求处理的路径。
即规定，对哪个URL path 调用对应的app！

.. note::

    如果使用wsgiref.make_server创建一个server，只有一个app，那么所以的请求都会使用该app处理！
    可以参考 :ref:`wsgi 基础<wsgi_basic>`

.. [#] https://www.ustack.com/blog/demoapi2/
.. [#] http://blog.csdn.net/sonicatnoc/article/details/6539716


webob库
=======

WebOb is a Python library that provides wrappers around the WSGI request environment, and an object to help create WSGI responses. The objects map much of the specified behavior of HTTP, including header parsing, content negotiation and correct handling of conditional and range requests. 

来看例子：

.. literalinclude:: /_static/src/webob_test.py
    :linenos:

可以看到，myfunc,myfunc2的接口不是wsgi规范定义的。但是，通过wsgify包装后，他们
已经是wsgi app，并可启动、响应http请求！

::

	root@juno-controller:/smbshare/paste_test# curl   http://localhost:9999/dumm
	hi!
	root@juno-controller:/smbshare/paste_test# curl   http://192.168.60.254:9999/dumm
	<html>
	 <head>
	  <title>403 Forbidden</title>
	 </head>
	 <body>
	  <h1>403 Forbidden</h1>
	  Access was denied to this resource.<br /><br />
	 </body>

先了解webob的简单用法，等分析openstack源码遇到更高级用法时再近些分析！

routes库
========

restful程序的一大特点是url和app对应起来，但是wsgi规范和webob并没有
解决这个问题。这就是routes库解决的问题，来看官网说明：

Routes is a Python re-implementation of the Rails routes system for mapping URL’s 
to Controllers/Actions and generating URL’s. Routes makes it easy to create pretty 
and concise URL’s that are RESTful with little effort.

来一个例子：

.. literalinclude:: /_static/src/webob_routes-2.py
    :linenos:

.. important::

	Each route in `mapper` must specify a 'controller', which is a
	WSGI app to call.  You'll probably want to specify an 'action' as
	well and have your controller be an object that can route
	the request to the action-specific method.
	
	通过这段文字可以知道，我们mapper.connect()的controller参数就是和url关联的
	WSGI app。如果指定了action参数，那么请求会路由到该特定的方法！
  

---------------------

参考
=====

.. [#] http://f.dataguru.cn/thread-127360-1-1.html
.. [#] http://askubuntu.com/questions/140360/kvm-kernel-module-error

