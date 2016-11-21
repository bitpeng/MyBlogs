.. _wsgi_basic:



WSGI基础
#########


.. contents:: 目录
   :depth: 3

--------------

.. note::

    参考： http://agiliq.com/blog/2013/07/basics-wsgi/

一系列术语
==========

.. attribute:: web server

   指软件程序，它从客户端(一般指浏览器)接受请求，然后返回一个Response。特别需要注意，web
   server不创建Response，而是仅仅返回请求。所以一个server需要和web
   app进行通信，而web app才是创建Response的实体。

.. attribute:: web app

   web server会从该处取得Response。web
   app的职责是根据url创建Response然后返回给server。server仅仅将该Response返回给客户端。

.. attribute:: wsgi

   wsgi是一个接口，一个规范或者一系列规则集合。他不是一个软件，也不是一个框架。

wsgi之所以出现，是因为 app 需要和 server 进行通信。wsgi 指定 app 端和 server 端
的需要实现的接口规范，这样他们就可以互相通信。所以一个兼容 wsgi 的 server 
可以和一个兼容wsgi的app通信。

在wsgi架构中，\ **WSGI app**\ 要求能够是被调用的，并提供给 server 。
所以当 server 接收到一个 request 时，可以调用web app生成 Response。

.. code:: python

    #web_app.py
    from wsgiref.simple_server import make_server

    def application(environ, start_response):
        path = environ.get('PATH_INFO')
        if path == '/':
            response_body = "Index"
        else:
            response_body = "Hello"
        status = "200 OK"
        response_headers = [("Content-Length", str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]

    httpd = make_server(
        '127.0.0.1', 8051, application)

    httpd.serve_forever()

在命令行执行\ ``python web_app.py``,然后访问http://127.0.0.1:8051/和http://127.0.0.1:8051/abcd，第一个返回index，第二个返回hello。

逐步分析代码： 

* ``make_server``\ 函数可以用来创建一个兼容wsgi的server； 
* 我们创建一个可调用服务application，你可以认为它是一个web app； 
* ``make_server``\ 创建了一个兼容wsgi的server，所以在该例子中，httpd是web server； 
* ``make_server``\ 的第三个参数需要传递web app，web server从该app里取得Response。

当请求来到时，监听8051端口的server会调用web
app，在该例子里是application。


web app代码的更多细节:

* web app也需要是兼容wsgi的；
* server会用两个参数调用web app，所以web app需要带有两个参数，这是web app兼容wsgi的条件之一； 
* 第一个参数包含request的信息；示例中，我们从中获取请求的path； 
* 第二个参数应该是可调用的，app使用该参数通知server Response Status，还可以用来设置Response headers，这是web app兼容wsgi的第二个条件； 
* 我们同时满足使得application兼容wsgi的两个条件； 
* 其次application创建了一个Response，并返回给wsgi server； 
* 最终，server返回该Response给客户端；

我们可以很方便的切换到其他的web server。例如使用gunicorn代替wsgiref。

注释掉web\_app.py最后两行，然后：

::

    gunicorn web_application:application --bind=localhost:8051

同样：

- 我们需要告诉gunicorn他所调用的application；
- gunicorn所监听的端口和host；
- 在实例中，我们的可调用app在文件web\_app.py中，所以在命令行中使用：\ ``web_application:application``


wsgi 中间件
============

wsgi 中间件也是一个可调用的app，它接受另一个app为参数，并返回包装后的app对象，从而实现
其他额外的功能。

请看例子，Upperware就是一个中间件，它的作用是把simple_app返回的内容全部转换成大写：

.. code-block:: python

	def simple_app(environ, start_response):
		status = '200 OK'
		response_headers = [('Content-type','text/plain')]
		start_response(status, response_headers)
		return ['Hello world!\n']

	class Upperware:
	   def __init__(self, app):
		  self.wrapped_app = app

	   def __call__(self, environ, start_response):
		  for data in self.wrapped_app(environ, start_response):
			 return data.upper()

	from wsgiref.simple_server import make_server

	application = Upperware(simple_app)
	httpd = make_server('127.0.0.1', 8051, application)
	httpd.serve_forever()

特别注意
=========

.. important::

	wsgi只规定了web server和web app之间如何通信。但是，一般而言，不同的URL path应该用不同的app进行
	处理，但是wsgi对此并未规定。就上面的例子而言，由于只定义了一个app，因此，只要IP 和端口正确的所有
	http 请求，都将由simple_app处理。

	对于如何将不同的URL path分发给不同的app进行处理，这就是其他库的任务了。如典型的pasteDelopy，它
	就是通过配置文件定义实现，在openstack等项目中使用！


Unicode问题
===========

请看pep-3333 wsgi规范关于unicode 的描述：

HTTP协议不直接支持unicode，它的接口也不支持。因此app需要处理encoding/decoding：
所有的strings(server传来的和传递给server的)都只能是str类型或者bytes类型，决不能
是unicode。在需要string对象而返回unicode对象的地方，结果是未定义的！

同样需要指出：传递给 start_response 回调函数的strings(作为HTTP 响应状态码和
头部)需要服从RFC-2616的编码规定。因此：他们只可能是ISO-8859-1字符集或者RFC-2047多媒体编码！

在python平台上，str和StringType类型都是基于unicode的(如：Jython, IronPython, Python3);
该规范里涉及到的所有strings只能包含 ISO-8859-1 编码规则列出的码点。
wsgi app 提供包含任意其他unicode字符集或者码点的strings都是严重错误。
类似的，servers或者gateway也不应该给一个app提供包含其他unicode字符集的strings


再次强调：该规范里涉及的所有string对象只能是str或者StringType，而不能是unicode 或者UnicodeType；
即使有些平台str或者StringType对象支持超过 8bits/每字符，也可能只有低8
位字符可用。

如果该规范里涉及到的值为”bytestrings“(如：wsgi.input, 传递给write(),或者由app yield产生)，
他们的类型只能是bytes(在Python3中)，或者str(以前的Python版本！) 


参考
========


.. note::

    和上一篇结合起来，非常好，可以对wsgi有很深入的理解。

    http://ivory.idyll.org/articles/wsgi-intro/what-is-wsgi.html


另外还可以参考：

http://www.letiantian.me/2015-09-10-understand-python-wsgi/

https://segmentfault.com/a/1190000003069785
