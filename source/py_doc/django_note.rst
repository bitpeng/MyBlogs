.. _django_note:


#############
django笔记
#############

:Date: 2017-04-06


django学习/阅读代码/horizon开发相关过程笔记，防止遗忘。


.. contents:: 目录

--------------------------


HttpRequest对象
===============

待补充

.. figure:: /_static/images/kvm_error.png
   :scale: 100
   :align: center

   待插图

模型
======

django模型，是在django项目中定义类对象(一般在models.py文件中)，然后通过 ``python manage.py syncdb`` 命令，生成数据库表。

我们也可以利用已有的数据库。在django book集成已有的数据库一章中提到，通过配置django项目setting.py文件，
具体来说，主要是DATABASE_NAME，DATABASE_ENGINE，DATABASE_USER，DATABASE_PASSWORD，
DATABASE_HOST，和DATABASE_PORT这些配置信息，然后使用如下的命令生成自省模型。

::

    python manage.py inspectdb > mysite/myapp/models.py

可是OpenStack Horizon项目来说，我在setting.py配置文件中并没有找到相关上述配置项信息。但是，
对于数据库名为openstack_dashboard中的表，的确可以通过上述命令生成相应的models.py。看来，
上述配置项应该在其他地方，可惜我并没有找到！


数据查询
++++++++++

获取表所有记录：

::

    ModelsTable.objects.all()

过滤查询：

::

    ModelsTable.objects.filter(name='ceilometer-api')
    
    # 相当于select from ModelsTable where name like 'ceilometer'
    ModelsTable.objects.filter(name__contains='ceilometer')
    
查询单条记录，假如查询结果有多条，会发生异常：

::

    ModelsTable.objects.get(id=1)
    
.. [#] 详细论述了django数据查询 网址：http://python.usyiyi.cn/django/topics/db/queries.html



---------------------

参考
=====

.. [#] http://djangobook.py3k.cn/appendixH/

