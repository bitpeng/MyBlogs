wsgi基础
========

tags： Python wsgi

--------------

[TOC]

--------------

    参考： http://agiliq.com/blog/2013/07/basics-wsgi/

一系列术语

-  **web
   serve**\ ：指软件程序，它从客户端(一般指浏览器)接受请求，然后返回一个Response。特别需要注意，web
   server不创建Response，而是仅仅返回请求。所以一个server需要和web
   app进行通信，而web app才是创建Response的实体。
-  web app： web server会从该处取得Response。web
   app的职责是根据url创建Response然后返回给server。server仅仅将该Response返回给客户端。
-  wsgi：是一个接口，一个规范或者一系列规则集合。他不是一个软件，也不是一个框架。

wsgi之所以出现，是因为app需要和server进行通信。wsgi指定app端和server端的需要实现的接口规范，这样他们就可以互相通信。所以一个兼容wsgi的server可以和一个兼容wsgi的app通信。

在wsgi架构中，\ **WSGI
app**\ 要求能够是被调用的，并提供给server。所以当server接收到一个request时，可以调用web
app生成Response。

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

逐步分析代码： \*
``make_server``\ 函数可以用来创建一个兼容wsgi的server； \*
我们创建一个可调用服务application，你可以认为它是一个web app； \*
``make_server``\ 创建了一个兼容wsgi的server，所以在该例子中，httpd是web
server； \* ``make_server``\ 的第三个参数需要传递web app，web
server从该app里取得Response。

当请求来到时，监听8051端口的server会调用web
app，在该例子里是application。

web app代码的更多细节 \* web app也需要是兼容wsgi的； \*
server会用两个参数调用web app，所以web app需要带有两个参数，这是web
app兼容wsgi的条件之一； \*
第一个参数包含request的信息；示例中，我们从中获取请求的path； \*
第二个参数应该是可调用的，app使用该参数通知server Response
Status，还可以用来设置Response headers，这是web
app兼容wsgi的第二个条件； \*
我们同时满足使得application兼容wsgi的两个条件； \*
其次application创建了一个Response，并返回给wsgi server； \*
最终，server返回该Response给客户端；

我们可以很方便的切换到其他的web server。例如使用gunicorn代替wsgiref。

注释掉web\_app.py最后两行，然后：

::

    gunicorn web_application:application --bind=localhost:8051

同样： \* 我们需要告诉gunicorn他所调用的application； \*
gunicorn所监听的端口和host； \*
在实例中，我们的可调用app在文件web\_app.py中，所以在命令行中使用：\ ``web_application:application``

wsgi导论
========

    和上一篇结合起来，非常好，可以对wsgi有很深入的理解。
    http://ivory.idyll.org/articles/wsgi-intro/what-is-wsgi.html

另外还可以参考：

http://www.letiantian.me/2015-09-10-understand-python-wsgi/

https://segmentfault.com/a/1190000003069785
