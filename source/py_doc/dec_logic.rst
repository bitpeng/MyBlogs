.. _dec_logic:


########################
Python 装饰器逻辑
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


Python装饰器可以理解，可是每次阅读代码时，都要使用转换过的方法才能顺着看。
因此这里作以下总结。以方便快速阅读代码


.. contents:: 目录

--------------------------


类装饰器
========

::

	# 类装饰器
	@webob.dec.wsgify
	def app1(req):
		return webob.Response("Hello, app1")

类似于：

::

	app1_obj = wsgify(app1)

为了描述方便，将原始的定义的方法称为app1, 包装后返回的对象称为
app1_obj, 包装后，app1为类对象，因此wsgify 类一定定义了__call__方法。
调用app1_obj(……)时，实际上是先调用__call__ 方法，然后一般在
__call__方法中再次调用原始的函数(app1函数)！


函数装饰器
==========

::

	# 函数装饰器
	def dec_func1(path):
		'''  
		A @get decorator.

		@get('/:id')
		def index(id):
			pass
		'''
		def _decorator(func):
			func.__web_route__ = path 
			func.__web_method__ = 'GET'
			return func 
		return _decorator

	@dec_func1('/:id')
	def app2(id):
		pass

调用逻辑类似于：

::

	app2_func = dec_func1(app2)

这种情况, dec_func1一定定义了闭包。
app2_func实际上是内层闭包函数(这里是_decorator函数)，因此调用
app2_func(……)相当于执行内层闭包函数！



类装饰器带参数
==============

::

	# 类装饰器
	@webob.dec.wsgify(RequestClass=webob.Request)
	def app3(req):
		return webob.Response("Hello, app1")

类似于:

::

	app3_obj = wsgify(RequestClass=webob.Request)(app3)

再类似于：

::

	wsgify_obj = wsgify(RequestClass=webob.Request)
	app3_obj = wsgify_obj(app3)

这种情况，要求wsgify定义了__call__方法，并且wsgify_obj(app3)
的执行结果一般应该返回一个可调用对象。

