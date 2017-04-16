.. _horizon_develop:


########################
Horizon 二次开发指南
########################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::
    在OpenStack云平台中，horizon是一个相对比较简单的项目，是入门OpenStack开发的一个比较好的切入点，
    本文档是自己对OpenStack dashboard进行二次开发过程的总结。


.. contents:: 目录

..
   section-numbering::


--------------------------


Horizon结构
===========

如图1所示的仪表盘结构，最上的导航栏为 :class:`dashboard` 元素，左侧为panel，中间为tab和tabgroup。
因此，我们第一步尝试自己创建一个panel。

.. figure:: /_static/images/dashboard.PNG
   :scale: 100
   :align: center

   图1：dashboard结构



快速生成panel
=============

OpenStak horizon为我们提供两个命令startpanel和startdash，供我们快速生产panel和dashboard。我自己试了很多次startdash命令，
新添加的dashboard命令无法显示，可能还需要修改某些地方的配置文件。而startpanel命令，测试成功。

::

    cd /opt/cecgw/csmp/openstack_dashboard/dashboards/admin_traffic_monitor
    python /usr/share/openstack-dashboard/manage.py startpanel test_panel -d openstack_dashboard.dashboards.admin_traffic_monitor


该命令运行成功后，会在admin_traffic_monitor目录下生产一个test_panel目录，包含该panel的所有信息。
然后进行以下操作：

- 编辑admin_traffic_monitor的dashboard.py文件，在panel属性中加上‘test_panel’元素，
- 编辑test_panel/panel.py文件， 将dashboard.Admin_Traffic_Monitor.register(Test_Panel)
  中的Admin_Traffic_Monitor更改成和dashboard.py中类名一致。
- 重启apache2，刷新页面，就可以看到效果。

.. figure:: /_static/images/start_panel.png
   :align: center

   图：添加panel效果


dashboard汉化
========================

如效果图可以看到，新添加的panel是英文显示的，可以通过如下步骤进行汉化：

- 编辑dango.po文件；
- 执行转换并重启服务器；

.. code:: shell

    cd /opt/cecgw/csmp/openstack_dashboard/locale/zh_CN/LC_MESSAGES/
    vi django.po
    msgfmt --statistics --verbose -o django.mo django.po
    /etc/init.d/apache2 restart

.. figure:: /_static/images/translation.png
   :align: center

   图：dashboard元素汉化



manage.py文件
=============

horizon项目是基于django的，而manage.py文件是django项目的一个重要文件，可以用来生成模型，自省模型，
还可以用来开启django环境的命令行。

基于ubuntu部署openstack时，manage.py文件位于： ``/usr/share/openstack-dashboard``

同步模型和自省模型：

::

    cd /usr/share/openstack-dashboard
    python manage.py syncdb

manage.py 文件还有一个重要作用是用来调试，是最近才发现的一个新功能！后调试一节中讲解。

settings.py
=============

horizon是基于Django的，因此它也有一个最重要的Django文件。公司内基于ubuntu-14.04-LTS部署的juno版openstack，
settings.py文件绝对目录为：/usr/share/openstack_dashboard/openstack_dashboard/settings.py

调试
=====

前端调试
+++++++++

对前端开发不是太熟，在dashboard开发中，我使用的是firebug插件，配合在js文件中使用console打印信息，
用来跟踪变量，查看变量状态等。


后端调试
+++++++++

horizon项目中，对于前端发起的http请求，有时要跟踪跟踪后端的处理流，查看变量值等。由于horizon项目
使用apache2进行部署，apache会把后端的操作记录在相关的日志中，因此我们可以使用log库，配合以下命令，
跟踪变量状态；但是对于处理流程分析，我目前还没有发现好的方法，都是根据代码逻辑进行分析。

horizon项目中，前端展示基于django模板系统，业务逻辑由python编写。因此在业务逻辑中，假如想查看变量的
某些信息，可以使用 ``print "+++===+++: %s"%args`` (之所以加上 ``+++===+++`` 是为了从Apache2 error.log
中快速过滤出自己添加的print信息)。然后在apache2的错误日志中，查看变量信息！

::

    cd /var/log/apache2
    tail -f error.log | fgrep "+++===+++"

使用manage.py调试
+++++++++++++++++

horizon 项目基于apache部署时，假如开发过程horizon代码发生
改动，需要重启apache2服务器，然后刷新页面，不太方便也比较麻烦！

其实django 框架的manage.py 文件也具有一定的调试功能。
我们只需要利用 manage.py启动web 服务即可！

::

    service apache2 stop
    cd /usr/share/openstack_dashboard
    python manage.py runserver 0.0.0.0:80

也可以不用关闭apache2服务器，只需要用另外一个没有使用的端口即可！
这种方式，在浏览器中输入ip:8080进行访问。

::

    cd /usr/share/openstack_dashboard
    lsof -i :8080
    python manage.py runserver 0.0.0.0:8080

通过 ``python manage.py runserver 0.0.0.0:80`` 启动服务，
终端会输出很多的信息。不方便查看，因此，我们可以把所以
输出重定向到一个文件，然后进行过滤查看即可！(个人开发时
使用该功能，可很方便的查看horizon项目变量信息。)


::

    python manage.py runserver 0.0.0.0:80 &> /smbshare/horizon.log
    tail -f /smbshare/horizon.log | fgrep "+++===+++"

.. figure:: /_static/images/manage_runserver.png
   :scale: 100
   :align: center

   运行开发模式服务器

.. figure:: /_static/images/filter_args.png
   :scale: 100
   :align: center

   过滤，查看变量信息


其他问题
=========

这一小节对horizon二次开发中常遇到的问题坐下记录。

权限错误
+++++++++

horizon权限问题遇到多次，具体错误信息可以通过 tail -f /var/log/apache2/error.log 命令查看。
在测试自己维护的调试信息库，还有snmp监控时都遇到过。使用 chmod 666/777 file/dir -Rn 修改权限，
错误消失！

.. figure:: /_static/images/permission_denied.png
   :scale: 100
   :align: center

   修改代码重启后权限错误


---------------------

.. [#] http://www.360doc.com/content/13/1114/19/8504707_329234716.shtml
.. [#] http://blog.csdn.net/bpingchang/article/details/37728415

