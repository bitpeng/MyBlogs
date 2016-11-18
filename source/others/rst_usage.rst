.. rst_usage:

rst 用法自我总结
#################


.. contents:: 目录

--------------------------



锚点链接
========

.. _link_text:

:ref:`点击链接<link_text>`


代码相关
========

普通代码定义：

::

	code here

高亮代码定义1：

.. code-block:: python
	:linenos:
	
	code here

高亮代码定义2：

.. code:: python

	code here

引用代码文件：

::

	.. literalinclude:: example.py
		:language: python
		
		code here


引用图片
========

::

	.. figure:: /_static/images/kvm_error.png
	   :scale: 100
	   :align: center

	   KVM启动虚拟机错误

注释
=====

::

	..
		这是注释
		这也是注释

..
	这是注释
	这也是注释
