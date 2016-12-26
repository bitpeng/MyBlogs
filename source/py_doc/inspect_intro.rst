.. _inspect_intro:


########################
python inspect 模块
########################

**date: 2016/12/26-14-40**

.. contents:: 目录

--------------------------



这里简要记录下 Python inspect 模块的用法。

OpenStack 组件使用了非常多的python库，包括标准模块和第三方模块。
之前自己在分析源码时，遇到不熟悉的库，总想把该库的方方面面都弄
清楚，结果这就造成自己分析 nova 组件的进度非常之慢。因此尝试换
一种方式，对于不熟悉的模块，把该模块在OpenStack组件中涉及到的用法
熟悉一下，后续有机会再补充完整。


inspect.stack
=============

对于 nova 组件，在 /var/log/nova 目录下都会有对应的 nova-\*.log 日志文件，
分析 nova/openstack/common/log.py 组件时，这是通过 :func:`inspect.stack`
实现的。来看源码(为了方便输出调试信息，我对源码进行了更改！):

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



