.. _rabbitmq_doc:


########################
[翻译] rabbitmq教程
########################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::
    本文档整理翻译自rabbitmq官方文档，通过六个例子阐述消息队列的相关概念，以及它的Python pika库接口。另外：对于一些不好直译的表达，本文均给出它的原始词汇。一些专有名词或者技术术语，一般都不予以翻译！

    Website：http://www.rabbitmq.com/getstarted.html


.. contents:: 目录



--------------------------

先决条件
========================

该教程假定RabbitMQ已经安装，并且该服务已经在本机启动，服务端口为5672.
假如你使用不同的主机，端口或证书，代码连接设置时需要作相应的调整！


获取帮助
========================

假如你对该教程有任何疑问，可以通过https://groups.google.com/forum/#!forum/rabbitmq-users邮件列表联系我们。


Hello, world
========================


RabbitMQ是一个消息中间件。它的主要思想很简单：接收和转发消息。
你可以把它想象成邮局：当你往邮筒投邮件时你确信邮递员最终将把邮件给接
收者。用这个隐喻(metaphor)，rabbitmq是邮筒，邮局和邮递员。   

Rmq和邮局的主要区别是rmq不处理纸质文件，取而代之它接收、保存和转发二进制数据：消息。

Rmq和消息传送，通常会使用一些术语。

产生意思不过是发送，一个发送消息的程序就是生产者。


.. figure:: /_static/images/rabbitmq_01.png
   :scale: 100
   :align: center


队列是信箱的另一个名字，它在rabbitmq里。虽然消息在rabbitmq和你的应用之间流动，
但是他们只能保持在队列里。队列不受任何限制的约束，它可以保存你想要保存的任何消息。
它本质上就是一个无限的缓冲区，许多生产者可以发送消息给一个队列，许多消费者可以从
一个队列里获取数据。队列正如它的名字，就是这样刻画的。

消费者和接收有一个相近的意义，一个消费者就是一个等待接收消息的程序。


Hello World
+++++++++++++++++

我们的“hello，world”程序不会太复杂：它发送消息，接收并且打印在屏幕上。
为了这样做，我们需要两个程序：一个发送消息，另一个接收并打印之。
我们所有的设计看起来是这样的。

.. figure:: /_static/images/rabbitmq_02.png
   :scale: 100
   :align: center

生产者发送消息到hello队列里，消费者从队列里接收消息。


Sending
+++++++++++++++++

.. figure:: /_static/images/rabbitmq_03.png
   :scale: 100
   :align: center

我们的程序将向队列发送一条简单的消息。我们所要做的第一件事就是和rabbitmq 服务建立连接。

.. code:: python

    #!/usr/bin/env python
    import pika

    connection = pika.BlockingConnection(pika.ConnectionParameters(
                   'localhost'))
    channel = connection.channel()

我们现在通本地的中间件建立了连接。如果我们想要同在不同机器上的中间件建立连接，我们只需要具体指出他的名字或者ip既可。
下一步，在发送之前，我们需要确保接收者队列存在，如果我们网不存在的队列发送消息，rabbitmq就会丢弃它。让我们建立一个队列，命名为hello：

::

    channel.queue_declare(queue='hello')

在此处，我们准备好发送消息，我们的第一条消息只包含hello，将发往hello队列。
在rabbitmq中，消息从来不能直接发给队列，它将通过交换机发送。但是我们不要被细节拖累(drag down)了。在本系列的第三部分，你将读到更多的关于交换机的知识。我们所需要做的就是怎样使用一个默认的交换机，它有一个空串标识。这个交换机是特殊的：它允许我们具体指定消息去往哪个队列。队列名字需要在routing_keying参数中指定。


::

    channel.basic_publish(exchange='',
                          routing_key='hello',
                                                body='Hello World!')
    print " [x] Sent 'Hello World!'"


在程序结束之前，我们需要确保网络缓冲区被刷新，并且我们的消息正确的交付给了rabbitmq。我们可以通过轻轻的关闭连接做到。

::

    connection.close()

.. tip::

    **如果不能发送消息：**

    如果这是你第一次使用rabbitmq，并且你没有看到发送的消息，然后你可能抓耳挠腮想哪里出错了。可能中间件开启时没有足够的磁盘空间（默认至少需要1G）因此拒绝接受消息。检查中间件的日志文件，消除限制。配置文件文档将教你怎样设置disk_free_limit


Receiving
+++++++++++++++++

第二个程序将从队列取得消息，并在屏幕打印。
同样，首先我们需要连接Rabbitmq服务器。负责连接上rabbitmq的代码和以前是以前的。
下一步，和之前一样，是确保队列存在。使用queue_declare声明一个队列很重要，我们可以这个命令多次，但是只有一个被创建。

::

    channel.queue_declare(queue='hello')

你可能会问，为什么我们又一次声明该队列。在之前的代码中，我们已经声明过了。如果我们确定队列已经存在，我们可以不那样做。例如：如果send.py程序在运行，但是我们不知道哪个程序将会先运行。这种情况下，重复声明队列是良好的实践方式！

.. figure:: /_static/images/rabbitmq_04.png
   :scale: 100
   :align: center

Listing queue
-----------------------

你可能希望查看rabbitmq有哪些队列，并且有哪些消息。你可以使用rabbitmqctl命令(z特权用户)

::

    $ sudo rabbitmqctl list_queues
    Listing queues ...
    hello    0
    ...done.
    (omit sudo on Windows)


从队列中获取消息要复杂。它通过往一个队列里订阅回调函数。当收到消息时，这个回调函数会被pika库调用。在我们的例子中，这个函数将会打印消息内容。

.. code:: python

    def callback(ch, method, properties, body):
        print " [x] Received %r" % (body,)

下一步，我们需要告知rabbitmq，这个特殊的回调函数会从我们的hello队列中获取消息。

.. code:: python

    channel.basic_consume(callback, queue='hello', no_ack=True)


为了该命令成功，我们必须确保我们想要订阅的队列存在。幸运的是这很容易，我们上面已经通过queue_declare 创建了一个队列。
No_ack参数将在后面描述。

最后，我们进入一个无限循环，等待数据。并且在必要的时候运行回调函数。


::

    print ' [*] Waiting for messages. To exit press CTRL+C'
    channel.start_consuming()

Putting it together
+++++++++++++++++++++++

Full code for send.py:

.. literalinclude:: /_static/src/rabbitmq_send.py
   :linenos:

Full receive.py code:


.. literalinclude:: /_static/src/rabbitmq_receive.py
   :linenos:


现在我们可以再终端运行程序，首先，我们用send.py程序发送消息。

::

    $ python send.py
    [x] Sent 'Hello World!'

生产者程序在每一个运行后都会终止，让我们接收。

::

    $ python receive.py
    [*] Waiting for messages. To exit press CTRL+C
    [x] Received 'Hello World!'

激动人心！我们已经通过rabbitmq发送了第一条消息。可能你已经注意到了，
receive.py 程序并没有退出。它将准备好接收更多的消息。可以按ctrl-C中断。

在另一个终端运行send.py程序。

我们已经学习了怎样通过一个命令队列收发消息。下一部分，我们将建立一个简单的工作队列。


Work queues
===========

Work Queues
++++++++++++++++

.. figure:: /_static/images/rabbitmq_05.png
   :scale: 100
   :align: center

第一篇教程种，我们写了个程序通过命名队列收发消息。这里，我们将创建一个工作队列，它将把很多费时的任务分发给多个worker.

工作队列的主要思想是避免直接做一个资源密集型任务，并且不得不等待它完成。相反我们较晚的调度该任务。我们把一个任务封装成消息，发往队列。工作进程在后台运行，取得任务并最终执行。当你运行多个工作进程时，任务将在他们之间共享。

在web应用中，这种思想是非常重要的。Web应用中，一个短期的http请求窗口期间并不能处理一个复杂的任务。


Prepaartions
++++++++++++++++

前一篇教程，我们发送一条包含hello，world 的消息。现在我们将发送代表复杂任务的字符串。我们没有一个真实的任务，比如一个需要重新计算尺寸的图像，一个需要被渲染的pdf文件，让我们通过使用time.sleep（）函数假装我们任务繁忙正在处理这些文件。我们用字符串中的点数来代表复杂度。每一点代表任务的一秒。如：一个用hello…描述的任务将用时3秒。

我们将简单改动之前的send.py文件，允许任意的消息通过commind line发送。这个程序将安排任务到工作队列，命名为new_task.py.


.. code:: python

    import sys

    message = ' '.join(sys.argv[1:]) or "Hello World!"
    channel.basic_publish(exchange='',
                          routing_key='hello',
                                                body=message)
    print " [x] Sent %r" % (message,)


Receive.py脚本同样需要一些改变：在消息中，它需要为每一个点用时一秒，它将从队列中获取消息，并且执行任务，称之为worker.py


.. code:: python

    import time

    def callback(ch, method, properties, body):
        print " [x] Received %r" % (body,)
        time.sleep( body.count('.') )
        print " [x] Done"



Round-robin dispatching
+++++++++++++++++++++++

工作队列的一个明显好处就是可以轻松的并行工作。如果我们创建一系列任务(a backlog of work)，我们可以通过增加更多的worker来轻松扩展。
首先，我们尝试同时运行2个worker.py脚本。他们将同时从工作队列取得任务。

你需要打开三个终端，2个运行worker.py脚本，代表着我们的两个消费者，C1和C2.

::

    shell1$ python worker.py
     [*] Waiting for messages. To exit press CTRL+C
    shell2$ python worker.py
     [*] Waiting for messages. To exit press CTRL+C


第三个终端，我们将发布一系列任务。一旦你开启了消费者程序，你就可以发布一系列消息。

::

    shell3$ python new_task.py First message.
    shell3$ python new_task.py Second message..
    shell3$ python new_task.py Third message...
    shell3$ python new_task.py Fourth message....
    shell3$ python new_task.py Fifth message.....


看看给worker转交了什么。

::

    shell1$ python worker.py
     [*] Waiting for messages. To exit press CTRL+C
     [x] Received 'First message.'
     [x] Received 'Third message...'
     [x] Received 'Fifth message.....'
    shell2$ python worker.py
     [*] Waiting for messages. To exit press CTRL+C
     [x] Received 'Second message..'
     [x] Received 'Fourth message....'

默认的，rabbitmq将会把每一条消息顺序的发送给下一个消费者。平均看来，每一个消费者都会获得相同数量的消息。这种分发消息的方式成为轮转(round robin)。开启三个或更多的workers试试。


Message acknowledgment
++++++++++++++++++++++

每一个任务都要话费好几秒。你可能怀疑当一个消费者开启一个耗时的任务，并只在做了部分时死亡将会发生什么。在我们的当前代码中，一旦rabbitmq递交消息给消费者，它就直接把消息中内存删除。这种情况下，如果一个worker死亡，我们将丢失刚刚处理的消息。我们同样会丢失所有发给这个worker但是未被处理的消息。

但是我们不想丢失每一个任务，如果一个workers死亡，我们想要任务被递交给另一个worker。

为了确保消息不会丢失，rabbitmq支持消息确认。Ack确认从消费者发出告知rabbitmq，某个消息已经收到并被处理。然后rabbitmq可以自由的删除。
如果消费者没有发出ack就死亡，rabbitmq将会认为消息没有被完全处理，然后递交给另一个消费者。这样，即使某个worker突然死亡，我们也能确保消息不会丢失。

没有什么消息超时机制；rabbitmq只会在和worker的连接断开后重新递交消息。这样假如处理一个很耗时的任务会有好处。

消息确认机制默认是打开的。在之前的例子，我们通过设置no_ack=True标志来显式关闭消息确认机制。一旦我们了某个任务，我们就可以清除该标志，并从worker发出一个合适的ack。

::

    def callback(ch, method, properties, body):
        print " [x] Received %r" % (body,)
        time.sleep( body.count('.') )
        print " [x] Done"
        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_consume(callback, queue='hello')

这里的代码我们能够保证，即使你使用CTRL-C杀死一个正在处理消息的worker，没有什么会丢失。Worker死亡之后，所有没有被确认的消息将会重新递交。


Forgotten acknowledgment 
----------------------------

Miss basic_ack是一种很常见很简单的任务，但是后果却很严重。当你的客户端终止后，消息会被重新递交(这看起来好像是随机重新递交)，但是rabbitmq将会吃掉越来越多的内存直到它不能发布任务没有被确认的消息。

为了调试该问题，你可以使用rabbitmqctl工具打印messages_unacknowledged域。

::

    $ sudo rabbitmqctl list_queues name messages_ready messages_unacknowledged
    Listing queues ...
    hello    0       0
    ...done.

Message durability
++++++++++++++++++

我们已经学习了怎样确保在消费者死亡时任务不会丢失。但是如果rabbitmq服务停止运行，我们的任务一样会丢失。

当rabbitmq停止或者崩溃后，它将丢失所有的队列和消息，除非你告诉他别那么做。为了确保消息不丢失，
需要做两件事：需要同时标记队列和消息为持久的。

首先，我们确保rabbitmq永不丢失队列，我们需要声明队列是持久的。

::

    channel.queue_declare(queue='hello', durable=True)

虽然这条命令式正确的，但是在我们的程序中不能工作。这是因为，我们已经声明了一个非持久化的
hello队列。Rabbitmq不允许你重新定义一个参数不同但已经存在的队列。它将返回一个错误！
但是有一个快速的解决方法(workaround)，让我们声明一个不同的队列，如task_queue.

::

    channel.queue_declare(queue='task_queue', durable=True)

这里，生产者和消费者程序代码需要同时改变。

这样，即使rabbitmq重启，task_queue队列也不会丢失。现在我们需要标记消息为持久的。通过将delivery_mode属性值设置为2既可！

::

    channel.basic_publish(exchange='',
                      routing_key="task_queue",
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

.. note::
    **消息持久化注解：**

    标记消息为持久化也不能完全保证消息不会丢失。尽管告知rabbitmq在磁盘保存消息，但是在
    rabbitmq接收消息和保存之前会有一个短暂的时间窗口。并且，rabbitmq不会为每一条消息执行
    fsync.所有可能导致cache被更新，但是没有同步写入磁盘。持久化保证不是健壮的，但是对于我
    们简单的任务队列来说，它足够了。如果你需要更强的保证，你可以使用发布-确认。


Fair dispatch
++++++++++++++

你可能发现了，分发方式没有完全按照我们想要的方式工作。例如，在有两个workers的解决方案中，当所有奇数任务很繁重，而偶数任务简单时，一个worker就会一直很繁忙，而另一个worker几乎不（hardly）做任何工作。但是rabbitmq并没有注意到这些，它还是均匀的分发消息。

发生这种情况是因为rabbitmq当队列里有消息它就仅仅分发消息。对于每一个消费者，它不看还有多少消息未被确认，它盲目的把妹第N个消息分发给第N个消费者。


.. figure:: /_static/images/rabbitmq_06.png
   :scale: 100
   :align: center

为了解决这个问题，我们可以通过basic.qos函数，设置prefetch_count=1。这就是告诉rabbitmq，不要在一段时间内给worker分发超过一个消息。换言之：在worker已经处理并发回前一个消息的确认之前，不要给他分发新消息。相反，rabbitmq将把消息分发给另一个不是很忙的worker。

::

    channel.basic_qos(prefetch_count=1)

.. note::

    **Note about queue size 队列长度注解**

    当所有的worker都繁忙时，你的队列可能被填满。(译注：当所有worker都繁忙，消息不分发给任务worker，这时假如再往队列里发布新消息，队列可能就会被填满。)你可能想监视这种情况，或者增加更多的worker，或者采取其他的策略。


Putting it all together
++++++++++++++++++++++++++

.. literalinclude:: /_static/src/rabbitmq_receive_2.py
    :linenos:

And our worker:


.. literalinclude:: /_static/src/rabbitmq_worker.py
    :linenos:

通过使用消息确认和prefetch_count，你可以设置一个工作队列。持久化可以确保在rabbitmq重启后认为依然存在。


 Publish/Subscribe
===================

.. important::
    该模式可以类比为广播、多播模式

    立刻发送消息给许多消费者


工作队列模式是假设，每一个任务是递交给某个确切的worker。而发布订阅方法完全不同：它把消息发送给多个消费者。

为了阐述这个模式，我们将建立一个简单地日志系统。包含两部分：第一个发出记录消息，而第1部分将接受并打印。

在该日志系统中，所有正在运行的接受程序拷贝(译注：即接收程序的多个样本，开启的多个进程)将获取消息。我们可以先运行一个接收者程序，直接在磁盘记录日志。同时，我们运行另一个接收者程序并在屏幕打印！

发布的消息将会广播给所有的接收者。


Exchanges
++++++++++++

前面我们通过队列发送和接收消息。现在介绍rabbitmq的消息机制。

快速回顾之前的教程：

- 生产者是一个发送消息的用户程序。
- 队列是一个保存消息的缓冲区。
- 消费者是一个接收消息的用户应用。

Rabbitmq的核心消息机制(messaging model)是：生产者从来不会直接给队列发送消息。（the producer never sends any messages directly to a queue）。实际上：生产者甚至经常都不知道消息是否会被递交给某个队列。

相反，生产者只会把消息发送给一个交换机，交换机是很简单的东西。它在一头从生产者接收消息，在另一头又把消息推送给队列。交换机需要确切指定当接收到一条消息时需要做什么。需要给某个特殊的队列么？还是需要给需要给所有的队列？或者还是丢弃它?这些规则在交换机类型中定义：


.. figure:: /_static/images/rabbitmq_07.png
   :scale: 100
   :align: center

有以下几种可以使用的交换机类型：direct,topic，header和fanout.我们讲述最后一种：fanout。让我们创建一个叫logs的交换机。

::

    channel.exchange_declare(exchange='logs', type='fanout')

Fanout 交换机很简单，它把接收到的消息发送给所有(它知道)的队列。这正是我们的额logger程序需要的。

List Exchanges
------------------

通过rabbitmqctl命令可以列出服务器上的交换机

::

    $ sudo rabbitmqctl list_exchanges
    Listing exchanges ...
    logs      fanout
    amq.direct      direct
    amq.topic       topic
    amq.fanout      fanout
    amq.headers     headers
    ...done.

列表里，有一些amq.*exchanges，和默认的交换机（没有被命名)。他们被默认创建，现在看起来还用不着他们。

Nameless  exchange
--------------------
之前的教程，我们队交换机一无所知，但是还是可以往队列发消息。这是因为我们使用了默认交换机，它通过空字符串标识。

::

    channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message)

交换机参数是交换机的名字。空字符串表示他是默认的或未命名的：如果存在，消息将会被routing_key路由至队列。

现在我们发布一个命名交换机

::

    channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)


Temporary queues
++++++++++++++++++

前面的教程种，我们使用了具名队列(还记得hello和task_queue吗？)。给队列命名很重要，我们需要给workers指定同样的名字。当你想在生产者和消费者之间共享队列，给队列命名是非常重要的。

但是我们的logger程序不是这种情况，我们想要接收所有的日志消息，而不是某个子集。同样，我们只对当前的消息流而不是旧消息感兴趣。为了解决这个问题，我们做2件事。

首先，不管何时连接上rabbitmq，我们需要一个新的空队列。所有我们需要给队列一个随机名字，或者最好是让rabbitmq服务器为队列选择一个随机名字。为queue_declare函数不提供queue参数可以做到这一点。

::

    result = channel.queue_declare()

这里，result.method.queue包含一个随机的队列名字，例如它可能看起来像：amq.gen-JzTY20BRgKO-HjmUJj0wLg.

然后，一旦消费者断开连接，队列需要被删除，通过设置exclusive标记即可。

::

    result = channel.queue_declare(exclusive=True)


Bindings
++++++++++++++++++


.. figure:: /_static/images/rabbitmq_08.png
   :scale: 100
   :align: center

我们已经创建了一个fanout交换机和一个队列，现在，我们需要告知交换机给我们的队列发送消息。交换机和队列之间的关系叫做一个binding

::

    channel.queue_bind(exchange='logs',
                   queue=result.method.queue)

现在，我们的logs交换机将会给我们的队列发消息了。

Listing bindings
------------------

可以使用rabbitmqctl列出已经存在的binding。



Putting it all together
+++++++++++++++++++++++

.. figure:: /_static/images/rabbitmq_09.png
   :scale: 100
   :align: center


发出日志消息的生产者程序，看起来和之前的没有太多的不同。最重要的变化是我们把消息发布给logs交换机而不是未命名交换机(默认交换机)。发送时我们需要提供一个routing_key ,但是他的值会被fanout交换机忽略。

.. literalinclude:: /_static/src/rabbitmq_src_1.py
   :linenos:

建立连接后，我们声明交换机。由于禁止给不存在的交换机发消息，这一步是必要的。

如果没有队列和交换机绑定，消息将会丢失。由于现在没有消费者，我们可以安全的丢弃消息，这并没有任何问题。

The code for receive_logs.py:

.. literalinclude:: /_static/src/receive_logs.py
   :linenos:

使用rabbitmqctl list_bindings你可以验证代码确实创建了我们想要的bindings和队列。

对结果的解释是很直观的，logs交换机出来的数据流向了服务器命名的两个队列。这也是我们所想要的。

为了监听消息的子集，接下来让我们学习教程4.


Router
======

前面我们构建了一个简单的日志系统，现在，我们将增加一个特性，只订阅消息的某个子集！

例如：我们只将严重的错误信息记录日志(保存在磁盘空间)。而在控制台输处所有消息。

Bindings
++++++++

在以前的例子中，我们已经创建了绑定，你可能这样调用代码：

::

    channel.queue_bind(exchange=exchange_name,
                   queue=queue_name)

绑定是交换机和队列之间的关系。可以这样理解：队列只对这个交换机的消息感兴趣！

绑定可以有其他额外的routing-key参数。为了避免同basic_publish参数混淆，我们称之为绑定键。我们可以创建一个带有键的绑定。

::

    channel.queue_bind(exchange=exchange_name,
                   queue=queue_name,
                   routing_key='black')

绑定键的含义取决于交换机的类型。Fanout交换机会直接忽视这个值！


Direct exchange
++++++++++++++++

之前的日志系统广播所有的消息给消费者。现在我们想根据日志的严重等级进行消息过滤。例如，我们可能想让把日志写进磁盘的程序只接收严重错误信息，这样可以不用在警告消息和通知消息浪费磁盘空间。

使用fanout交换机，并没有带来多少弹性，它只是盲目的广播。

我们将使用direct交换机。Direct交换机的路由算法很简单：消息只流进绑定键和该消息的routing_key 完全匹配的队列！

考虑下图：

.. figure:: /_static/images/rabbitmq_10.png
   :scale: 100
   :align: center

现在，我们看到direct交换机X绑定了两个队列。第一个队列的绑定键是orange，第二个有两个bindings，一个绑定的绑定键是black另一个绑定键是green

此种情况下：带有路由键orange的消息发布给交换机后将会路由给队列Q1.带有路由键black或green的消息将流向Q2，所有的其他消息将会丢弃。

Multiple bindings
+++++++++++++++++

.. figure:: /_static/images/rabbitmq_11.png
   :scale: 100
   :align: center

多个队列绑定同一个路由键是合法的。在我们的例子里，我们可以增加一个X和Q1的绑定，绑定键位black。此时：direct交换机将会像fanout一样，广播消息给所有匹配的队列。带有路由键black的消息将会同时递交给Q1和Q2.


Emitting logs
+++++++++++++

该模式下，我们将用direct交换机代替fanout。我们给日志提供严重等级作为路由键。这样接收程序就可以选择他所要的严重等级日志。

首先我们创建一个交换机

::

    channel.exchange_declare(exchange='direct_logs',
                         type='direct')

我们准备发消息

::

    channel.basic_publish(exchange='direct_logs',
                      routing_key=severity,
                      body=message)

为了简单，我们假定严重等级只有’info’,’warning’，’error’.

Subscribing
+++++++++++

我们将会为每一个我们感兴趣的严重等级创建一个新绑定。

::

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    for severity in severities:
        channel.queue_bind(exchange='direct_logs',
                           queue=queue_name,
                           routing_key=severity)


Putting it all together
+++++++++++++++++++++++

.. figure:: /_static/images/rabbitmq_12.png
   :scale: 100
   :align: center


.. literalinclude:: /_static/src/rabbitmq_src_2.py
   :linenos:


The code for receive_logs_direct.py:


.. literalinclude:: /_static/src/receive_logs_direct.py
   :linenos:


假如你只想保存“warning”和‘error’的日志信息到文件：

::

    $ python receive_logs_direct.py warning error > logs_from_rabbit.log

如果你想在你的屏幕上查看所有的消息。

::

    $ python receive_logs_direct.py info warning error
     [*] Waiting for logs. To exit press CTRL+C

发送错误日志消息只需输入：

::

    $ python emit_log_direct.py error "Run. Run. Or it will explode."
     [x] Sent 'error':'Run. Run. Or it will explode.'
    (Full source code for emit_log_direct.py and receive_logs_direct.py)

教程5将会根据模式来监听消息。


Topics
=========

之前我们改进了日志系统，我们没有用fanout交换机，它只能进行广播，取而代之，我们使用direct交换机，从而使选择性接收日志消息成为可能。

Direct同样存在限制：它不能根据多重标准进行路由！

在我们的日志系统中，我们可能既想根据消息严重等级，同时也根据日志源订阅消息。可能从unix工具syslog里得知这个概念，它(syslog)根据消息严重等级(info/warn/crit)和组件设施(auth/cron/kern)进行日志路由！

这给予我们极大的弹性，比如：我们像监听来自cron的严重错误日志，同时也监听来自kern的所有日志。

为了实现这一点，我们需要学习更加复杂的topic交换机。


Topic exchange
+++++++++++++++

发往topic交换机的路由不能包含任意的routing_key。它只能是一个单词列表，由.号分开。单词可以是任何东西，但通常他们指定和消息相关联的一些特性。合法的routing_key例子是：“stock.usd.nyse”，”quick.orange.rabbit”。routing key可以包含你想要的很多单词，上限是255字节。

绑定键需要时同样的形式。Topic交换机背后的逻辑和direct交换机是相似的：一个包含特定路由键的消息将递交给所有绑定了相匹配的绑定键的队列。但是，binding key有两个重要的特殊例外。

\* 号可以代替一个确切的单词；

#号可以代替0个或多个单词。

用例子解释这是最简单的。(译注：可以认为是正则匹配)


.. figure:: /_static/images/rabbitmq_13.png
   :scale: 100
   :align: center

在这个例子里，我们将发送描述动物的消息。消息包含一个routing key，路由键由三个单词，2个点号组成。Routing key形式如下："<celerity>.<colour>.<species>".

我们创建三个绑定，Q1和绑定键”*.orange.*”绑定，Q2的绑定键是"\*.\*.rabbit" and "lazy.#".

这些绑定可以总结如下：

- Q1对所有的橙色动物感兴趣；
- Q2想监听所有有关兔子和所有懒惰动物的消息

注意："lazy.pink.rabbit"只会递交给第2个队列一次，即使他匹配2个绑定。

假如我们打破约定，发送一个有一个单词或者四个单词的消息如"orange" or "quick.orange.male.rabbit"，会发生什么。这些消息不匹配任何绑定，会丢失。

另一方面："lazy.orange.male.rabbit"，虽然他有四个单词，但是它匹配最后一个绑定，会递交给第2个队列。


Topic Exchange
++++++++++++++

Topic交换机很强大，可以表现出其他交换机的行为。

当一个队列的binding key 是”#”，不管routing key 是什么，它都会接受消息。这像fanout交换机。

当特殊字符”*”和”#”不在绑定中使用，topic交换机的行为就像direct一样。


Putting it all together
+++++++++++++++++++++++

We're going to use a topic exchange in our logging system. We'll start off with a working assumption that the routing keys of logs will have two words: "<facility>.<severity>".

The code is almost the same as in the previous tutorial.

The code for emit_log_topic.py:


.. literalinclude:: /_static/src/emit_log_topic.py
   :linenos:


The code for receive_logs_topic.py:

.. literalinclude:: /_static/src/receive_logs_topic.py
   :linenos:


To receive all the logs run:

python receive_logs_topic.py "#"

To receive all logs from the facility "kern":

python receive_logs_topic.py "kern.*"

Or if you want to hear only about "critical" logs:

python receive_logs_topic.py "\*.critical"

You can create multiple bindings:

python receive_logs_topic.py "kern.*" "\*.critical"

And to emit a log with a routing key "kern.critical" type:

python emit_log_topic.py "kern.critical" "A critical kernel error"

这些程序很有趣，请记住，代码不能假定路由和绑定键。所有你需要处理多于2个routing key参数的情况

Some teasers:

- Will "*" binding catch a message sent with an empty routing key?
- Will "#.*" catch a message with a string ".." as a key? Will it catch a message with a single word key?
- How different is "a.*.#" from "a.#"?
-  “\*“绑定可以获取带有空routing key的消息吗？
-  “#”可以获取键是”..”的消息吗？它会获取键是单个单词的消息吗？
-  “a.*.#”和”a.#”有何不同。



Remote procedure call (RPC)
============================

在第二篇教程中，我们学习了，怎样通过工作队列把耗时的(time-consuming)任务分发给多个客户。

但是，假如我们需要在远程计算机上运行一个函数，并等待结果，该如何做？这是另外一个问题，这种模式通常被称为RPC。

该篇教程，我们通过RMQ构建一个RPC系统：一个客户端，和一个可扩展的RPC Server。由于我们没有什么耗时的任务需要被分发，因此我们通过建立一个模拟(dummy)RPC服务，该服务返回fibonacci数。


Client interface
++++++++++++++++++

为了阐述RPC 服务如何运行，我们将写一个简单的客户类。它暴露一个叫call公有方法，该方法发起一个RPC请求，然后阻塞，直到收到回复！

::

    fibonacci_rpc = FibonacciRpcClient()
    result = fibonacci_rpc.call(4)
    print "fib(4) is %r" % (result,)

.. note::

    **RPC注解**

    尽管RPC是一种相当常见的计算模式，但是它也有很多争议。当一个程序员不清楚一个函数调用是否为本地函数，或者它是否为一个慢速RPC时，问题出来了。类似的困惑会导致不确定的系统行为，并且会引入不必要的调试复杂度。非但不能简化软件系统，RPC的误用会导致不可维护的混乱代码(spaghetti code，意大利面条似的code)。

    切记，考虑以下建议：

    - 1、确保能显然的区分哪些函数调用时本地的哪些是RPC。
    - 2、编写系统文档，使组件之间的依赖关系很清晰。
    - 3、处理错误情况。当RPC服务器宕机很长时间时客户端应该如何做出反应。

    有疑问时请避免使用RPC。如果可以，你应该使用异步流水线代替RPC，结果同样会异步的推到下一个计算阶段。


Callback queue
---------------

通常来说，用RMQ来作RPC时简单的。客户端发送一个请求消息，并且一个服务器用一个应答消息回复。为了获取一个应答，客户端需要在发送请求时附带发送一个callback队列地址。

::

    result = channel.queue_declare(exclusive=True)
    callback_queue = result.method.queue

    channel.basic_publish(exchange='',
                          routing_key='rpc_queue',
                          properties=pika.BasicProperties(
                                reply_to = callback_queue,
                                ),
                          body=request)

    # ... and some code to read a response message from the callback_queue ...


.. tip::
    **Message properties**

    AMQP协议预先为一个消息定义了14种属性，大部分属性极少使用，以下属性是例外。

    delivery_mode：标记该消息为持久化的(值为2)或者临时的(任意其他值)。你可能在第二篇教程种还记得该属性。


Correlation id
---------------

在上面展示的方法中，我们建议为每一个RPC请求创建一个callback队列。可是这相当低效，幸运的是我们有一种更好的办法，只为每一个客户端创建一个callback队列。

可是这又带来了新问题，在一个队列中受到一个回复时，不清楚这个回复时属于哪个请求的。这时就需要使用correlation_id属性了。我们将为每一个请求设置一个唯一的值，然后当我们在callback队列中收到一个消息时，我们将查看这个属性值。通过这个值，我们可以正确匹配请求和应答，如果是一个未知的correlation_id值，我们可能丢弃该消息，它不属于我们的请求。

你可能会问，为什么我们要忽视callback队列中的未知消息呢，而不是通过错误宣告失败？这是因为server端可能存在的竞争条件。考虑这样一种情况，RPC服务器在给我们发出回答后，但是在给我我们发出ack确认消息之前宕机，虽然可能性小，但是并不是不可能。如果这种情况发生，重启的RPC服务器将会再一次处理请求。这就是为什么客户端需要优雅的处理重复消息，并且RPC作者需要在理论具有幂等性。

(译者注：计算机科学中的幂等性是指一次和多次请求某一个资源应该具有同样的副作用)


总结
+++++

.. figure:: /_static/images/rabbitmq_14.png
   :scale: 100
   :align: center


我们的RPC这样工作：

- 1、当客户端开启，它创建一个异步exclusive callback队列。（译者注：exclusive队列表示队列只能被队列创建者使用）
- 2、对于一个RPC请求，客户端发送一个消息，该消息包含两个属性：reply_to，该属性表示which is set to the callback队列（reply_to 属性相当于是callback队列的唯一编号）(译者注：此处没有正确理解所表达的意思)；correlation_id属性，它表示给每个请求设置一个唯一的编号。
- 3、请求发送给一个rpc_queue队列。
- 4、RPC worker(aka,又称作服务器)在rpc_queue队列上等待请求，当请求到达，它开始工作，并把结果(通过消息)发回给客户端，这一步是通过队列上的reply_to域实现的。（译者注：还记得吗，前面提到每一个消息请求都包含一个reply_to属性，请求消息发送到callback队列中，服务器从队列取回消息后，消息包含reply_to属性，即从哪个队列取得消息，再根据该属性把应答发给取得消息的队列）。
- 5、客户端在消息队列上等待应答，当应答出现，它检查correlation_id属性，如果该值和请求消息的匹配，它把应答返回给应用程序。


Putting it all together
+++++++++++++++++++++++

The code for rpc_server.py:

.. literalinclude:: /_static/src/rpc_server.py
   :linenos:

服务端代码是相当直观的：

第4行中，我们像以往一样，建立连接，声明队列。

第11行，我们定义Fibonacci函数。它假定只会有合法的非负整数输入。(不要期望该函数对大数还能正常工作，它可能是最慢的递归实现)

19行，我们为basic_consume声明callback，RPC服务器的核心，当请求到达时它就执行，它完成工作并且发回应答结果。

32行，我们可能希望运行更多的服务端进程，为了众多服务器之间的负载均衡，我们需要设置prefetch_count项。


The code for rpc_client.py:

.. literalinclude:: /_static/src/rpc_client.py
   :linenos:


客户端的代码稍微有点复杂：

7行，我们建立一个连接，信道，并且为返回结果声明一个互斥的callback队列。

16行，我们订阅callback队列，这样我们就可以收到rpc回复。

18行，on_response回调函数收到每个应答时就执行，它作非常简单的工作，对于每一个应答消息，它检查correlation_id属性是否是我们需要的。如果是，它把结果保存在self.response里，并且跳出消费循环。

23行，下一步，我们定义主调用函数：它处理真正的RPC请求。

24行，这个函数中，首先，我们产生一个唯一的correlation_id号并保存，on_response回调函数将会通过这个值捕捉合适的应答。

25行，下一步，我们发布请求消息。包含两个属性：reply_to 属性和correlation_id 属性。

32行，现在，我们开始等待，知道合适的应答消息到达。

33行，最终我们把应答消息返回给用户。


Our RPC service is now ready. We can start the server:

::

    $ python rpc_server.py
     [x] Awaiting RPC requests

To request a fibonacci number run the client:

::

    $ python rpc_client.py
     [x] Requesting fib(30)

展现的设计并非唯一的RPC服务实例，但是它有一些重要的优点：

- 1、如果rpc服务器太慢，你可以通过运行另外一个来加速。在新的终端运行另一个rpc_server.py既可。
- 2、在客户端，rpc只需发送和接收一条消息，无需使用queue_declare这样的同步调用。结果，对于每一个rpc请求，rpc客户端只需一个网络轮回。

我们的代码足够简单，并且没有尝试解决更复杂但也重要的问题，例如：

- 1、没有服务端在运行，客户端如何反应。
- 2、对于每一个rpc请求，客户是否需要超时时间
- 3、如果服务器故障并且发生异常，它是否应该通知客户端。
- 4、处理之前，为无效的输入消息提供保护(例如：检查约束)

如果你想尝试，你可能发现rabbitmq-management插件对查看队列很有用！



---------------------

参考
=====

.. [#] http://www.jb51.net/os/RedHat/189963.html

