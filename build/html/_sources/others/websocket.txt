.. _websocket:


########################
Django WebSocket
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. contents:: 目录

--------------------------

最近调研了下WebSocket技术，经过深究，对WebSocket技术的基本原理以及相关细节有了比较好的把握，
并利用dwebsocket模块在Django项目中测试向多个客户端代理(浏览器)同时推送消息。


websocket基础知识
==================

关于websocket的基本原理，互联网上有很多讲解，在此推荐 `看完让你彻底搞懂Websocket原理 <http://www.tuicool.com/articles/7zyMvy6>`_ ；

websocket握手连接过程
++++++++++++++++++++++

建立连接的握手
当Web应用程序调用new WebSocket(url)接口时，Browser就开始了与地址为url的WebServer建立握手连接的过程。

1. Browser与WebSocket服务器通过TCP三次握手建立连接，如果这个建立连接失败，那么后面的过程就不会执行，Web应用程序将收到错误消息通知。
2. 在TCP建立连接成功后，Browser/UA通过http协议传送WebSocket支持的版本号，协议的字版本号，原始地址，主机地址等等一些列字段给服务器端。
3. WebSocket服务器收到Browser/UA发送来的握手请求后，如果数据包数据和格式正确，客户端和服务器端的协议版本号匹配等等，就接受本次握手连接，并给出相应的数据回复，同样回复的数据包也是采用http协议传输。
4. Browser收到服务器回复的数据包后，如果数据包内容、格式都没有问题的话，就表示本次连接成功，触发onopen消息，此时Web开发者就可以在此时通过send接口想服务器发送数据。否则，握手连接失败，Web应用程序会收到onerror消息，并且能知道连接失败的原因。

这个握手很像HTTP，但是实际上却不是，它允许服务器以HTTP的方式解释一部分handshake的请求，然后切换为websocket数据传输
WebScoket协议中，数据以帧序列的形式传输。

..
    考虑到数据安全性，客户端向服务器传输的数据帧必须进行掩码处理。服务器若接收到未经过掩码处理的数据帧，则必须主动关闭连接。
    服务器向客户端传输的数据帧一定不能进行掩码处理。客户端若接收到经过掩码处理的数据帧，则必须主动关闭连接。
    针对上情况，发现错误的一方可向对方发送close帧(状态码是1002，表示协议错误)，以关闭连接。

借用网上的一个图，来表示websocket的连接状态。

.. figure:: /_static/images/websocket_connect.png
   :scale: 100
   :align: center

   websocket连接状态

客户端websocket
++++++++++++++++


下面，通过网址 ``http://redflag.f3322.net:6680/`` 来具体分析客户端websocket的相关知识要点。

在浏览器中打开 ``http://redflag.f3322.net:6680/`` ，这是一个简单的基于websocket的页面，
功能是服务器向所有的打开的页面推送rsyslog日志消息，保存页面源代码为wstest.html，
并简单改写然后进行测试，改写后的文件wstest.html如下：

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
    <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
    <script language="JavaScript">
    <!--
    locate = 0;
    function scroller() {
    if (locate !=500 ) {
    locate++;
    scroll(0,locate);
    clearTimeout(timer);
    var timer = setTimeout("scroller()",3);
    timer;
    }
    }
    // -->
    </script>
      <title>demo</title>
      <meta charset="utf8" />
    </head>
    <body OnLoad="scroller()">
        <div class="container">
        <br/> 
        <h1> Rsyslog Demo </h1>
         <div id="board"><div>
        </div>
      
      <script>
        var socket = new WebSocket('ws://' + "redflag.f3322.net:6680" + '/database/');

        socket.onopen = function open() {
          console.log('WebSockets connection created.');
        };

        socket.onmessage = function (message) {
          var dom = document.getElementById("board");
          //var log = document.createElement("p");
          //log.innerHTML = message.data;
          //dom.appendChild(log);
          $('#board').prepend('<p>' + message.data + '</p>');
        }

        if (socket.readyState == WebSocket.OPEN) {
          socket.onopen();
        }
      </script>

    </body>
    </html>

浏览器中打开该HTML文件，利用firebug进行抓包分析！截图信息如下：

.. figure:: /_static/images/web_wstest.png
   :scale: 100
   :align: center

   websocket页面抓包

结合wstest.html来看，页面加载时，js代码尝试会发起websocket连接(URL为：
``ws://redflag.f3322.net:6680/database/`` )，但是通过firebug抓包结果来看，
发起请求会将URL的模式部分替换成http(即URL为： ``http://redflag.f3322.net:6680/database/`` )，
同时该请求的首部，会有其他特殊的头信息字段，通知服务器这不是一个普通的HTTP请求，
而是websocket连接请求。

.. figure:: /_static/images/switch_proto.png
   :scale: 100
   :align: center

   服务器响应HTTP状态码

而服务器返回的101状态码，表示已经成功的进行了协议转换。

**这里特别注意：虽然websocket利用HTTP请求实现连接，但这就是为了兼容HTTP的握手规范，
websocket是一个全新的协议，和HTTP协议没太大关系。**


简而言之，**客户端发起websocket请求时，请求URL和普通的HTTP请求一样，但是在请求首部中，
会加上相关标识信息(首部Sec-WebSocket-Key，Sec-WebSocket-Version，Upgrade字段)，
然后服务端根据这些标识信息，进行协议切换并响应，此时websocket连接建立，
后续客户端、服务端可以同时利用该连接发送消息(而不像普通HTTP请求那样，服务端被动等待客户端发起连接并响应)。**

   
客户端WebSocket API
=====================

上面的例子中，涉及到部分WebSocket API，WebSocket提供一组可用于WebSocket编程的对象、方法和属性。

.. figure:: /_static/images/websocket_api.png
   :scale: 100
   :align: center

   WebSocket API

需要注意的是，readyState是一个只读属性，表示websocket的连接状态，他有下面四个可能值。

.. figure:: /_static/images/readyState.png
   :scale: 100
   :align: center


dwebsocket
============

由于不知道页面 ``http://redflag.f3322.net:6680/database/`` 后端对应的技术，
下面通过一个例子来，来探讨在Django中利用dwebsocket模块实现websocket技术！
主要参考了 `利用dwebsocket在Django中使用websocket <http://www.cnblogs.com/huguodong/p/6611602.html>`_ ；
但是该例子并没有实现，服务端向多个客户端推送消息的功能。下面介绍怎样实现这一功能：

编辑urls.py文件，加上下面这两行：

::

    url(r'^wstest$', views.ws_html),
    url(r'^websocket$', views.wstest),


::

    def ws_html(request):
        LOG_DEBUG('call generic http')
        return render(request, 'wstest.html')

    @accept_websocket
    def wstest(request):
        LOG_DEBUG('call wstest')
        if not request.is_websocket():#判断是不是websocket连接
            try:#如果是普通的http方法
                message = request.GET['message']
                return HttpResponse(message)
            except:
                return render(request,'wstest.html')
        else:
            clients.append(request.websocket)
            # 下面的for循环并不能删掉，否则无法给客户端推送消息，原因未知
            for message in request.websocket:
                request.websocket.send(message)

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
    <script src="/static/js/jquery.min.js"></script>
    <script language="JavaScript">
    <!--
    locate = 0;
    function scroller() {
    if (locate !=500 ) {
    locate++;
    scroll(0,locate);
    clearTimeout(timer);
    var timer = setTimeout("scroller()",3);
    timer;
    }
    }
    // -->
    </script>
      <title>django-websocket-demo</title>
      <meta charset="utf8" />
    </head>

    <body OnLoad="scroller()">
        <div class="container">
        <br/> 
        <h1> Django WebSocket Demo </h1>
      <div id="board"><div>

        </div>
      
      <script>
        //var socket = new WebSocket("ws://" + window.location.host + "/wstest");
        var socket = new WebSocket("ws://" + window.location.host + "/websocket");
        //var socket = new WebSocket("ws://" + window.location.host + "/echo");
        //var socket = new WebSocket('ws://' + window.location.host + '/echo/');

        socket.onopen = function open() {
          console.log('WebSockets connection created.');
        };

        socket.onmessage = function (message) {
          console.log('received websocket msg');
          $('#board').prepend('<p>' + message.data + '</p>');
        }

        if (socket.readyState == WebSocket.OPEN) {
          socket.onopen();
        }
      </script>
    </body>
    </html>


wstest函数的功能是，对于每一个websocket连接请求，保存websocket客户端。
后面，可以利用该clients客户端列表，进行消息推送。

.. note::

    使用dwebsocket时，需要特别注意的一点，就是发起websocket连接的URL不要和其他普通的http连接
    URL一样。否则可能会导致消息推送失败。

    当初自己在Django项目中测试时，就犯了这个错误(即在views.py只有wstest函数，没有ws_html函数。
    想利用wstest函数即返回页面，又同时处理websocket请求。)，
    结果怎么实验都无法推送消息。大家要特别这一这一点！


消息推送
=========

这里实现的是服务端向每个客户端推送消息，推送消息的时机很重要，一般而言，
客户端是依据状态变化，触发特定事件，然后进行消息推送。这里，为了方便，
是弄了一个定时任务，每几秒钟，依次向每一个websocket客户端推送消息。

::

    from apscheduler.scheduler import Scheduler
    sched = Scheduler()

    @sched.interval_schedule(seconds=1.5)
    def mytask():
        import uuid
        msg = "websocket test: recevied msg [{msg}] from server at <{time}>".format(
                    time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    msg=str(uuid.uuid4()))
        for i in clients:
            i.send(msg)

    sched.start()

刷新页面，就可以看到效果了。

.. figure:: /_static/images/websocket_test.png
   :scale: 100
   :align: center

根据firebug抓包信息，建立websocket连接后，客户端没有发起任何http请求，
但是依然可以源源不断的接收服务器主动推送的消息。

Apache部署
===========

上面的测试方式，使用的是Django自带的开发服务器( ``python manage.py runserver 0.0.0.0:port`` )。
在生产环境中，一般都是会基于apache/gunicorn等服务器部署(云审查项目基于apache部署)。
因此，需要在服务器上进行相应的配置以支持websocket。

激活模块 ``mod_proxy_wstunnel``, 以支持websocket连接。该模块于 ``mod_proxy`` 模块提供的服务。

::

    a2enmod mod_proxy_wstunnel

假如上述命令提示错误：ERROR: Module mod_proxy_wstunnel does not exist!那么试试用下面命令：

::

    a2enmod proxy_wstunnel

激活proxy_wstunnel模块后，参考了大量的资料，都没有配置成功。目前云审查项目基于apache2部署时，
还暂时没有实现websocket消息推送效果。错误信息截图如下：

.. figure:: /_static/images/websocket_ssl.png
   :scale: 100
   :align: center

.. figure:: /_static/images/socket_notfound.png
   :scale: 100
   :align: center

.. figure:: /_static/images/socket_notfound2.png
   :scale: 100
   :align: center


---------------------

参考
=====

.. [#] 关于怎么在Django中实现定时任务。网址：http://blog.csdn.net/hui3909/article/details/46652623
.. [#] 对websocket的原理及与HTTP的关系做了比较好的阐述。网址：http://www.tuicool.com/articles/7zyMvy6
.. [#] http://rfyiamcool.blog.51cto.com/1030776/1269232/
