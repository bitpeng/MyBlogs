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

* 编辑admin_traffic_monitor的dashboard.py文件，在panel属性中加上‘test_panel’元素，
* 编辑test_panel/panel.py文件， 将dashboard.Admin_Traffic_Monitor.register(Test_Panel)
  中的Admin_Traffic_Monitor更改成和dashboard.py中类名一致。
* 重启apache2，刷新页面，就可以看到效果。

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




---------------------

.. [#] http://www.360doc.com/content/13/1114/19/8504707_329234716.shtml

