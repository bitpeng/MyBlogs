.. _kombu:


#############################
kombu和消息队列总结
#############################

.. contents:: 目录

--------------------------

消息队列是OpenStack的重要组成部分，自己之前翻译过一篇 :ref:`rabbitmq教程 <rabbitmq_doc>` ，
但是看nova代码时，依然很多地方云里雾里，感觉不太清晰；并且该教程基于pika库，而OpenStack 默认
是使用kombu连接rabbitmq服务器，因此自己重新了解了下kombu库，并总结。

该文档是结合文档、代码示例再加上自己的理解整理而成，可能存在不准确的地方，欢迎指正！


术语
=====

.. attribute:: Producers

    Producers给exchanges发送消息。
    
.. attribute:: Exchanges

    消息发送给exchages。交换机可以被命名，可以通过路由算法进行配置(注：个人理解是，
    可以在声明交换机时，指定交换机名字和交换机类型，如 ``topic``)。
    
    **交换机通过匹配消息的 routing_key 和 binding_key来转发消息，binding_key 是consumer
    声明队列时与交换机的绑定关系。**

.. attribute:: Consumers

    消费者声明一个队列、并和某个交换机绑定，然后从队列中接收消息！

.. attribute:: Queues

    队列接收发往交换机的消息，**它由消费者声明。**

    **注：在pika库中，队列可以重复声明，重复声明队列时，只有一个会被创建，
    但是，不能重复声明类型不同的队列！**

.. attribute:: Routing keys

    每个消息都有一个routing_key，对 routing_key 的解释取决于交换机类型。
    AMQP 标准定义了四种交换机类型(注：``topic``，``fanout``，``direct``，``header``)。
    还可以自定义类型。

    - ``direct`` : 消息的 routing_key 属性和消费者的 routing_key 相同才递交消息；
    - ``fanout`` : 总是递交消息，即使队列和交换机banding没有 routing_key；
    - ``topic`` : 通过某种语义匹配模式匹配消息的 routing_key；消息的 routing_key 
      可以通过点号 ``.`` 分割，还可以包括两种特殊字符：:attr:`*`, :attr:`#` 。
      :attr:`*` 可以匹配一个单词，:attr:`#` 可以匹配0个或多个单词。
      
      **注：这段对topic交换机的描述来源于 kombu 官网，和 rabbitmq官网描述有一些出入。
      rabbitmq官网中，topic交换机，消息的 routing_key 是确切的，然后 交换机和
      和队列的 banding_key 可以包含该两个特殊字符。到底哪种描述是正确的，目前还不清楚。**


通过amqp收发消息模型
====================

通过amqp 收发消息，上面的描述已经很清晰了。这里再简单重复下：

- 消息从来不直接发送给队列，甚至 Producers 都可能不知道队列的存在。
  消息是发送给交换机，给交换机发送消息时，需要指定消息的 routing_key 属性！
- 交换机收到消息后，根据 交换机的类型，或直接发送给队列 (fanout)，
  或匹配消息的 routing_key 和 队列与交换机之间的 banding_key ; 而topic类型
  交换机匹配时，具有一些额外的特性，可以根据一些特殊字符进行匹配。
  如果匹配，则递交消息给队列！
- Consumers 从队列取得消息；

`即：消息发布者 Publisher 将 Message 发送给 Exchange 并且说明 Routing Key。
Exchange 负责根据 Message 的 Routing Key 进行路由，将 Message 正确地
转发给相应的 Message Queue。监听在 Message Queue 上的 Consumer 将会从 Queue 中
读取消息。Routing Key 是 Exchange 转发信息的依据，因此每个消息都有一个 Routing Key 
表明可以接受消息的目的地址，而每个 Message Queue 都可以通过将自己想要接收的 Routing Key 
告诉 Exchange 进行 binding，这样 Exchange 就可以将消息正确地转发给相应的 Message Queue。`

其他要点
========

待补充...

代码示例
========

示例一
+++++++

公共文件 :file:`kombu_entity.py`

::

    #!/usr/bin/env python
    # coding:utf-8

    from kombu import Exchange, Queue

    #定义了一个exchange
    #task_exchange = Exchange('tasks', type='direct')
    task_exchange = Exchange('tasks_fanout', type='fanout')

    #在这里进行了exchange和queue的绑定，并且指定了这个queue的routing_key
    task_queue = Queue('piap', task_exchange, routing_key='suo_piao')
    #task_queue = Queue('piap', task_exchange)

消息发送端 :file:`kombu_send.py`

::

    #!/usr/bin/env python
    # coding:utf-8

    from kombu import Exchange, Queue
    from kombu import Connection
    from kombu.messaging import Producer
    from kombu.transport.base import Message

    from kombu_entity import task_exchange
    #task_queue = Queue('piap', task_exchange, routing_key='suo_piao')


    connection = Connection('amqp://guest:httc123@10.10.10.10:5672//')
    channel = connection.channel()

    message=Message(channel, body='Hello Kombu')

    producer = Producer(channel, exchange=task_exchange)
    producer.publish(message.body, routing_key='suo_piao')
    #producer.publish(message.body)

消息接收端 :file:`kombu_recv.py`

::

    #!/usr/bin/env python
    # coding:utf-8

    from kombu import Connection
    from kombu.messaging import Consumer
    from kombu_entity import task_queue

    import logging
    logging.basicConfig(level=logging.DEBUG)

    #connection = Connection("amqp://guest:httc123@10.10.10.10:5672/")
    connection = Connection("amqp://guest:httc123@localhost:5672/")
    channel = connection.channel()

    def process_media(body, message):#body是某种格式的数据，message是一个Message对象，这两个参数必须提供
        print "recv: %s"%body
        message.ack()

    # 定义回调函数的两种方式。
    # 定义消费者，并定义回调函数！
    #consumer = Consumer(channel, task_queue)
    #consumer.register_callback(process_media)

    # 也可以在定义消费者对象时直接传递回调参数。
    consumer = Consumer(channel, task_queue, callbacks=[process_media])
    consumer.consume()

    while True:
        try:
            connection.drain_events()
        except KeyboardInterrupt:
            #connection.release()
            print "stopped"
            break

.. error::

    这个示例程序有一点问题：在 kombu_entity.py 中定义了 fanout 交换机，然后开启
    两个 kombu_recv.py 进程，但是然后运行 kombu_send 发送消息。这里两个接收进程
    并没有都收到消息，而是使用轮转分发的方式。待解决！

示例二
+++++++

该示例来源于 kombu 官网。可是，我在 ubuntu-14.04 Linux 下运行该示例代码，遇到一些小问题，
经过修改，可用正确运行。主要更改地方如下：

- 取消更改相对导入；
- client 端注释掉压缩参数；

公共文件 :file:`queues.py`

::

    from kombu import Exchange, Queue

    task_exchange = Exchange('tasks', type='direct')
    task_queues = [Queue('hipri', task_exchange, routing_key='hipri'),
                   Queue('midpri', task_exchange, routing_key='midpri'),
                   Queue('lopri', task_exchange, routing_key='lopri')]

消息接收端 :file:`worker.py`

::

    #!/usr/bin/env python
    from kombu.mixins import ConsumerMixin
    from kombu.log import get_logger
    from kombu.utils import kwdict, reprcall

    #from .queues import task_queues
    from queues import task_queues

    logger = get_logger(__name__)


    class Worker(ConsumerMixin):

        def __init__(self, connection):
            self.connection = connection

        def get_consumers(self, Consumer, channel):
            return [Consumer(queues=task_queues,
                             accept=['pickle', 'json'],
                             callbacks=[self.process_task])]

        def process_task(self, body, message):
            fun = body['fun']
            args = body['args']
            kwargs = body['kwargs']
            logger.info('Got task: %s', reprcall(fun.__name__, args, kwargs))
            try:
                fun(*args, **kwdict(kwargs))
            except Exception as exc:
                logger.error('task raised exception: %r', exc)
            message.ack()

    if __name__ == '__main__':
        from kombu import Connection
        from kombu.utils.debug import setup_logging
        # setup root logger
        setup_logging(loglevel='INFO', loggers=[''])

        with Connection('amqp://guest:httc123@localhost:5672//') as conn:
            try:
                worker = Worker(conn)
                worker.run()
            except KeyboardInterrupt:
                print('bye bye')

消息发送端 :file:`client.py`

::

    #!/usr/bin/env python

    from kombu.pools import producers

    #from .queues import task_exchange
    from queues import task_exchange

    priority_to_routing_key = {'high': 'hipri',
                               'mid': 'midpri',
                               'low': 'lopri'}


    def send_as_task(connection, fun, args=(), kwargs={}, priority='mid'):
        payload = {'fun': fun, 'args': args, 'kwargs': kwargs}
        routing_key = priority_to_routing_key[priority]

        with producers[connection].acquire(block=True) as producer:
            producer.publish(payload,
                             serializer='pickle',
                             #compression='bzip2',
                             exchange=task_exchange,
                             declare=[task_exchange],
                             routing_key=routing_key)

    if __name__ == '__main__':
        from kombu import Connection
        #from .tasks import hello_task
        from tasks import hello_task

        connection = Connection('amqp://guest:httc123@localhost:5672//')
        send_as_task(connection, fun=hello_task, args=('Kombu', ), kwargs={},
                     priority='high')

:file:`tasks.py` 文件

::

    def hello_task(who="world"):
        print("Hello %s" % (who, ))

以下是运行结果：

.. figure:: /_static/images/kombu_recv.png
   :scale: 100
   :align: center

   kombu 运行结果

另外需要注意的是：我尝试把 hello_task 函数放在 client.py 文件中定义，结果
运行时，总是提示如下错误。目前还不知道原因，待探讨。

::

    root@allinone-v2:/smbshare/oslo-test/msg# ./worker.py 
    Connected to amqp://guest@localhost:5672//
    Can't decode message body: AttributeError("'module' object has no attribute 'hello_task'",) (type:'application/x-python-serialize' encoding:'binary' raw:'<read-only buffer ptr 0x1bf3c9f, size 71 at 0x7f5bcf2b02b0>'')

在 kombu 的基础上，后续会继续熟悉 oslo.messaging。另外，Python导入问题遇到多次，也会
抽空彻底熟悉下。

---------------------

参考
=====

.. [#] https://kombu.readthedocs.io/en/latest/introduction.html
.. [#] http://blog.csdn.net/hackerain/article/details/7875614
.. [#] http://blog.csdn.net/gaoxingnengjisuan/article/details/9623529
