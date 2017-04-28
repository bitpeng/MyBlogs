.. _django_middleware:


######################################
django中间件和openstack用户重登录分析
######################################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^
    开始尝试读openstack源码，把阅读源码过程总结下来，以作参考。有不正确或严谨的地方，欢迎指正。

.. note::


    这一部分，分析的是openstack的用户重登录机制：简而言之，在规定的未使用时限后，
    系统断开会话或者重新鉴别用户 ，系统应提供时限的默认值；

.. contents:: 目录

--------------------------


代码定位
========


以下是系统超时自动退出时的提示：

.. figure:: /_static/images/timeout_logout.png
   :scale: 100
   :align: center

   超时自动退出


然后在openstack里，是根据django.po文件，然后对显示信息进行翻译。查找出"会话超时"提示对应的英文：

.. figure:: /_static/images/find_timeout.png
   :scale: 100
   :align: center



.. figure:: /_static/images/timeout_en.png
   :scale: 100
   :align: center

   查找显示信息对应的英文文本


可以看到，文本注释处已经提示了在middleware.py文件中。于是继续查找middleware.py文件：

.. figure:: /_static/images/find_timeout_en.png
   :scale: 100
   :align: center

   查找middleware文件

至此，已经找到重登陆的代码为路径为：horizon/middleware.py


django中间件原理
================

查看middleware的代码，发现它是一个中间件，利用中间件来处理会话超时重登录，因此，这里有必要理解下django中间件的原理。

Django 处理一个 Request 的过程是首先通过中间件，然后再通过默认的 URL 方式进行的。
我们可以在 Middleware 这个地方把所有Request 拦截住，用我们自己的方式完成处理以后直接返回Response。
因此了解中间件的构成是非常必要的。


它的主要作用，是在有些场合，需要对Django处理的每个request都执行某段代码。
这类代码可能是在view处理之前修改传入的request，或者记录日志信息以便于调试，等等。
在这些场合，事先使用中间件对每一个http请求进行拦截和预处理，是非常有必要的。


.. important::

    简言之，中间件是django框架提供的一种机制，利用该机制，我们可以拦截每一个http请求，并进行预处理。
    以达到我们想要的功能。

    我们可以自己定义中间件。另外，dango框架自身也定义了很多常用的中间件。

安装中间件
++++++++++

要启用一个中间件，只需将其添加到配置模块的 MIDDLEWARE_CLASSES 元组中。
在 MIDDLEWARE_CLASSES 中，中间件组件用字符串表示： 指向中间件类名的完整
Python路径。 例如，下面是 django-admin.py startproject 创建的缺省 MIDDLEWARE_CLASSES :

::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
         'django.contrib.sessions.middleware.SessionMiddleware',
         'django.contrib.auth.middleware.AuthenticationMiddleware',
    )

Django项目的安装并不强制要求任何中间件，如果你愿意， MIDDLEWARE_CLASSES 可以为空。


.. warning::

    这里中间件出现的顺序非常重要。 在request和view的处理阶段，Django按照 
    MIDDLEWARE_CLASSES 中出现的顺序来应用中间件，而在response和异常处理阶段，
    Django则按逆序来调用它们。 也就是说，Django将 MIDDLEWARE_CLASSES 视为
    view函数外层的顺序包装子： 在request阶段按顺序从上到下穿过，而在response则反过来。

中间件方法
++++++++++

我们可以定义中间件方法的一个或者多个，可以定义的中间件方法如下：

- 初始化方法

  ::

      Initializer: __init__(self) __init__(self)

  出于性能的考虑，每个已启用的中间件在每个服务器进程中只初始化 一 次。 
  也就是说 __init__() 仅在服务进程启动的时候调用，而在针对单个request处理时并不执行。


- Request预处理函数

  ::

    process_request(self, request) process_request(self, request)

  这个方法的调用时机在Django接收到request之后，但仍未解析URL以确定应当运行
  的view之前。 Django向它传入相应的 HttpRequest 对象，以便在方法中修改。


  .. important::

      .. figure:: /_static/images/pr_return.png
         :scale: 100
         :align: center

         函数返回与处理流程


- View预处理函数

  ::

     process_view(self, request, view, args, kwargs) process_view(self, request, view, args, kwargs)

  这个方法的调用时机在Django执行完request预处理函数并确定待执行的view之后，但在view函数实际执行之前。


- Response后处理函

  ::

    process_response(self, request, response) process_response(self, request, response)


- Exception后处理函数

  ::

    process_exception(self, request, exception) process_exception(self, request, exception)


代码细节
========

理解了中间件的工作原理，再来看代码细节，就很显然了。如图所示代码：

.. figure:: /_static/images/preq_func.png
   :scale: 100
   :align: center

   重登陆拦截预处理函数

对于每一个请求，django根据会话，得出上一次活动时间，并计算时间戳是否大于超时时间，如果大于，则
页面直接重定向到登录页面，后续的view调用等都会忽略；如果没有超时，则只需要简单的更新一下上一次活动时间，
接下来会按照正常流程处理。


Horizon 用户登录流程分析
=========================

下面对用户登录horizon的流程进行分析。

- 用户输入IP地址，根据setting.py ROOT_URLCONF配置项来决定根URL映射函数；

  .. figure:: /_static/images/root_urlconf.png
     :scale: 100
     :align: center

     openstack_dashboard/setting.py ROOT_URLCONF 配置项

- 根据URL匹配调用view处理函数(splash 函数。)

  .. figure:: /_static/images/url_map.png
     :scale: 100
     :align: center

     openstack_dashboard/urls.py

- 根据request session判断用户是否认证(请求中间件拦截，判断是否会话失效，这里不予考虑)，
  如果认证，则重定向到用户主界面；否则就加载模板系统，显示登录主界面；

  .. figure:: /_static/images/splash.png
     :scale: 100
     :align: center

     openstack_dashboard/views.py

  .. figure:: /_static/images/splash_html.png
     :scale: 100
     :align: center

     horizon/templates/splash.html 模板include表单模板

- 用户输入登录信息，登录；

- django框架表单数据校验；

  .. figure:: /_static/images/clean_f1.png
     :scale: 100
     :align: center

     表单数据校验：openstack_auth/form.py

  .. note::

    - 表单数据检验，注意可以使用clean_message方法来校验每一个表单属性，
      也可以使用clean 方法整体校验。
    - 表单校验clean函数，需要返回原始数据(cleaned_data)，否则会发生数据丢失。

- 假如数据校验成功，则提交表单，根据表单action 属性匹配映射处理函数。

  .. figure:: /_static/images/form_action.png
     :scale: 100
     :align: center

     登录页面，表单action属性。

  .. error::

      _login.html 表单继承 model_from1.html，并重写action 属性，但是{% url 'login' %} 最后怎么转换成"auth/login"，
      还需要进一步的分析。

      .. figure:: /_static/images/model_form1.png
         :scale: 100
         :align: center

         基类表单模板action属性

      .. figure:: /_static/images/model_form1.png
         :scale: 100
         :align: center

         _login.html 模板表单重写action 属性

  .. tip::

      {% url 'login' %}最后怎么转换成"auth/login"的过程已经理清，这里涉及到django中的name参数。
      
      .. code-block:: python

        # openstack_auth/urls.py
        urlpatterns = patterns(
            'openstack_auth.views',
            url(r"^testlogin/$", "login", name='dlogin'),

      .. figure:: /_static/images/testlogin.png
         :scale: 100
         :align: center

         页面显示代码

      ::
        
        # 魔板文件重写form_action属性！
        {% block form_action %}{% url 'dlogin' %}{% endblock %}
  

      页面模板使用{%url 'dlogin' %}转换url，所以总是转换成该名字对应的URL。
  
  .. [#] 论述了django URL name参数的用法及其意义。http://www.cnblogs.com/no13bus/p/3767521.html

- URL截断，分级URL匹配；

  .. figure:: /_static/images/url_include_1.png
     :scale: 100
     :align: center

     URL include 截断匹配

  .. figure:: /_static/images/auth_url.png
     :scale: 100
     :align: center

     URL分级匹配

  .. important::

     每当Django遇到 include() 时，它将截断匹配的URL，并把剩余的字符串发往包含的URLconf作进一步处理。

     include 通常用于网站目录分类处理，使项目中urls高度统一。

- 调用login处理函数和keystone认证后端，进行处理；

  .. figure:: /_static/images/auth_backend.png
     :scale: 100
     :align: center

     setting.py 认证后端项

流程图
======

这是自己根据上面的分析，绘制的一个简单流程图！

.. figure:: /_static/images/openstack_login.png
   :scale: 100
   :align: center

   处理逻辑和流程图

---------------------

参考
=====

.. [#] http://djangobook.py3k.cn/2.0/chapter17/
.. [#] http://lukejin.iteye.com/blog/599783
.. [#] http://www.52ij.com/jishu/1174.html
.. [#] http://www.cnblogs.com/daoluanxiaozi/p/3320618.html
.. [#] http://www.nowamagic.net/academy/detail/13281811

