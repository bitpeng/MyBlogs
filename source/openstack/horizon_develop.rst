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
    在OpenStack云平台中,horizon是一个相对比较简单的项目，是入门OpenStack开发的一个比较好的切入点，
    本文档是自己对OpenStack dashboard进行二次开发过程的总结。


.. contents:: 目录

..
   section-numbering::


--------------------------


Horizon结构
========================

如图1所示的仪表盘结构，最上的导航栏为dashboard元素，左侧为panel，中间为tab和tabgroup。
因此，我们第一步尝试自己创建一个panel。

.. figure:: /_static/images/dashboard.PNG
   :scale: 100
   :align: center

   图1：dashboard结构



快速生成panel
========================

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



---------------------

.. [#] http://www.360doc.com/content/13/1114/19/8504707_329234716.shtml
