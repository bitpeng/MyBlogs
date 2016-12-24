.. _periodic_task_1:

OpenStack定时任务分析(1)
########################

OpenStack 定时任务实现由两种实现方法，一种是通过 periodic_task 函数装饰器，
另外一种是由 :class:`DynamicLoopingCall` 和 :class:`FixedIntervalLoopingCall`
类通过协程来实现。主要用到的是 :class:`eventlet.event.Event` 类！让我们
首先来看看该类的用法。

::

    from eventlet import event
    import eventlet
    import time
    evt = event.Event()
    def baz(b):
        print "begin sleeping..."
        time.sleep(10)
        evt.send(b + 1)
        print "awake again!!!"

    _ = eventlet.spawn_n(baz, 3)
    print evt.wait()



根据官网文档，event设queue差不多，但是有两个不同：

- 调用 send() 不会交出自己的cpu时间
- send() 只能被调用一次

event主要用于在不同协程间传递返回值。比如我协程A需要等协程B做了某件事后的结
果，那么我协程A可以建立了一个event evt，然后调用evt.wait()就会开始等待。协程
B把事情做好后运行evt.send(XXX)（注意，由于都在一个线程中，所以获取这个evt甚
至不需要锁），这个时候协程A的evt.wait()代码就可以往下运行了，并且Hub会把相关的结果给它。

.. note::

    以上例子，通过 spawn_n() 函数启动一个新协程，但是假如不执行最后
    的 evt.wait()，那么 baz() 函数不会执行，结果没有任何输出。个人猜想
    是，协程是主动让出cpu，假如不执行 evt.wait() 当前程序不会让出cpu，
    那么新开启的协程也就没有机会调度运行。然后程序结束，直接退出，因此
    不会有任何输出。当然，这只是个人猜想，得抽时间，好好熟悉下协程的
    原理！

有了上面的简单例子作为基础后，我们利用 OpenStack 的 :class:`FixedIntervalLoopingCall`
创建一个定时任务。来看例子：

::

    #!/usr/bin/env python2

    #from nova import utils
    from nova.openstack.common.loopingcall import FixedIntervalLoopingCall
    from nova.openstack.common.loopingcall import LoopingCallDone
    #import inspect
    import eventlet

    count = 0

    def panda(tagline):
        global count
        count += 1
        print "#", count, "Panda.", tagline
        if count >= 3:
            #raise utils.LoopingCallDone
            print "Looping call Done, bye..."
            raise LoopingCallDone

    periodic = FixedIntervalLoopingCall(panda, "hello world!")
    #periodic.start(interval=0.8753)
    periodic.start(1, 2)
    periodic.wait()

来看看程序运行结果：

::

    root@allinone-v2:/smbshare# python periodic_fun.py
    # 1 Panda. hello world!
    2016-12-24 23:23:33.346 10839 WARNING nova.openstack.common.loopingcall [-] task <function panda at 0x7f5c5e2ac578> run outlasted interval by 1.00 sec
    # 2 Panda. hello world!
    2016-12-24 23:23:35.351 10839 WARNING nova.openstack.common.loopingcall [-] task <function panda at 0x7f5c5e2ac578> run outlasted interval by 1.00 sec
    # 3 Panda. hello world!
    Looping call Done, bye...

在程序中，我们设置定时任务执行三次。现在根据这个例子，来
分析下 :class:`FixedIntervalLoopingCall` 的源码:

::

    class LoopingCallBase(object):
        def __init__(self, f=None, *args, **kw):
            self.args = args
            self.kw = kw
            self.f = f
            self._running = False
            self.done = None

        def stop(self):
            self._running = False

        def wait(self):
            return self.done.wait()

    class FixedIntervalLoopingCall(LoopingCallBase):
        """A fixed interval looping call."""

        def start(self, interval, initial_delay=None):
            self._running = True
            done = event.Event()

            def _inner():
                if initial_delay:
                    greenthread.sleep(initial_delay)

                try:
                    while self._running:
                        start = _ts()
                        self.f(*self.args, **self.kw)
                        end = _ts()
                        if not self._running:
                            break
                        delay = end - start - interval
                        if delay > 0:
                            LOG.warn(_LW('task %(func_name)s run outlasted '
                                         'interval by %(delay).2f sec'),
                                     {'func_name': repr(self.f), 'delay': delay})
                        greenthread.sleep(-delay if delay < 0 else 0)
                except LoopingCallDone as e:
                    self.stop()
                    done.send(e.retvalue)
                except Exception:
                    LOG.exception(_LE('in fixed duration looping call'))
                    done.send_exception(*sys.exc_info())
                    return
                else:
                    done.send(True)

            self.done = done

            greenthread.spawn_n(_inner)
            return self.done

- 首先，实例化 :class:`FixedIntervalLoopingCall` 对象，保存协程要执行的函数，函数参数等；
- 然后执行 :func:`periodic.start(1, 2)` , 注意，执行该函数时，只是设置 interval, initial_delay
  参数，并利用闭包函数新建一个协程。此时，inner 函数还并没有机会投入运行！
- 主控程序 periodic.wait(), 让出CPU，接下来的，_inner 函数有机会执行，并统计函数执行时间，
  依据时间差进入睡眠状态，等待下一次调度执行！

.. tip::

    根据这个例子，我们可以知道，假如定时任务执行后，除非定时任务
    执行完成，否则代码 ``periodic.wait()`` 会永远阻塞。可是 OpenStack 组件一般
    有很多定时任务，那么他们是如何做到同时执行的呢。这个问题待结合OpenStack相关代码
    进行分析，待完成。

    初步猜想，可能是在线程中启动协程。这样就可以开启多个定时任务，待验证！
