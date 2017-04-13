.. _os_lib:


########################
Python Library
########################


.. contents:: 目录

--------------------------

OpenStack各组件使用了非常多的python库，包括标准模块和第三方模块。
之前自己在分析源码时，遇到不熟悉的库，总想把该库的方方面面都弄清楚，
结果这就造成自己分析nova组件的进度非常之慢。因此尝试换一种方式，
对于不熟悉的模块，把该模块在OpenStack组件中涉及到的用法熟悉一下，后续有机会再补充完整。

对于比较复杂的库，或者笔记篇幅大的，则会另起一篇文章在单独的blog中记录下来！

对于日常工作中接触到的Python模块，也是如此处理！

inspect
========

**date: 2016/12/26-14-40**

这里简要记录下Python inspect模块某些函数的用法。

inspect.stack
++++++++++++++

对于 nova 组件，在 /var/log/nova 目录下都会有对应的 nova-\*.log 日志文件，
分析nova/openstack/common/log.py源码可以知道，这是通过 :func:`inspect.stack`
实现的。来看源码(为了方便输出调试信息，我对源码进行了更改！)：

::

    def _get_binary_name():
        #stack = inspect.stack()[-1][1]
        stack = inspect.stack()
        b = os.path.basename(stack[-1][1])
        print "+++===+++ stack: %s"%stack
        return b

下面是运行时，打印的堆栈信息：

::

    [(<frame object at 0x7fa5692e2938>, '/usr/lib/python2.7/dist-packages/nova/openstack/common/log.py', 211, '_get_binary_name', ['    stack = inspect.stack()\n'], 0),
    (<frame object at 0x7fa56936a620>, '/usr/lib/python2.7/dist-packages/nova/openstack/common/log.py', 228, '_get_log_file_path', ['        binary = binary or _get_binary_name()\n'], 0),
    (<frame object at 0x18fb910>, '/usr/lib/python2.7/dist-packages/nova/openstack/common/log.py', 493, '_setup_logging_from_conf', ['    logpath = _get_log_file_path()\n'], 0),
    (<frame object at 0x7fa5692e2770>, '/usr/lib/python2.7/dist-packages/nova/openstack/common/log.py', 427, 'setup', ['        _setup_logging_from_conf(product_name, version)\n'], 0),
    (<frame object at 0x7fa571e64d00>, '/usr/lib/python2.7/dist-packages/nova/cmd/scheduler.py', 37, 'main', ['    logging.setup("nova")\n'], 0),
    (<frame object at 0x7fa573361910>, '/usr/bin/nova-scheduler', 40, '<module>', ['        sys.exit(main())\n'], 0)
    ]

可以看到，inspect.stack() 打印了调用处到程序启动的完整的堆栈信息。
它的每一项是一个元祖，每个元祖的具体条目信息如下：

::

    (frame_obj, 模块字符串, 调用行号, 函数， 语句信息)

因此，可以通过 inspect.stack()[-1][1] 获取服务启动时的服务名 ``nova-scheduler``

关于 inspect 模块的更多用法，可以参考:

.. [#] http://www.programcreek.com/python/example/737/inspect.stack


weakref
========

**date: 2017-3-7 16:00**

weakref弱引用模块的类和方法及其用法。

.. class:: weakref.ref(object[, callback])

ref创建一个弱引用对象，object是被引用的对象，callback是回调函数(当被引用对象被删除时的，会调用改函数)

.. class:: weakref.proxy(object[, callback])

proxy创建一个用弱引用实现的代理对象，参数同上。


那么weak.ref和weak.proxy有什么区别呢？请看例子：

::

    # coding:utf-8
    import weakref

    class TestObj(object):
        def __init__(self):
            self.i = "aaa"

        def __call__(self):
            return "call `%s` itself"%repr(self)

    a = TestObj()

    x = weakref.ref(a)
    print x
    print

    print a.i
    print x().i

    print
    print a()
    print x()()


    y = weakref.proxy(a)
    print
    print y
    print y.i
    print y()

.. code-block:: console

    root@allinone-v2:~# python /smbshare/weakref_test.py
    <weakref at 0x7f6c1a18af70; to 'TestObj' at 0x7f6c1a19add0>

    aaa
    aaa

    call `<__main__.TestObj object at 0x7f6c1a19add0>` itself
    call `<__main__.TestObj object at 0x7f6c1a19add0>` itself

    <__main__.TestObj object at 0x7f6c1a19add0>
    aaa
    call `<__main__.TestObj object at 0x7f6c1a19add0>` itself


根据运行结果，可以知道，使用ref创建弱引用x，需要使用x()才可以访问到原引用对象。

而 **proxy和ref的区别就是不需要()，可以像原对象一样地使用proxy访问原对象的属性。**

.. [#] http://blog.csdn.net/iamaiearner/article/details/9371315
.. [#] http://www.jianshu.com/p/0cecea85ae3b


sched
======

该模块是内置模块，源码也很少，才仅仅130行。是用于实现定时任务的。

读该库源码


sh
===

执行sh命令的库

读该库源码

stevedore
==========


sqlalchemy
===========
