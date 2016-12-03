.. _cloud_check:


########################
云平台服务器重启注意事项
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. contents:: 目录

--------------------------

由于服务器重启，导致云平台服务异常。因此写一个简单的文档，供参考!

核心服务状态检查
================

cinder服务
++++++++++

.. figure:: /_static/images/cinder_status.png
   :scale: 100
   :align: center

   cinder 服务状态正常

neutron服务
+++++++++++

.. figure:: /_static/images/neutron_status.png
   :scale: 100
   :align: center

   neutron 服务状态异常

nova服务
+++++++++++

.. figure:: /_static/images/nova_bad_status.png
   :scale: 100
   :align: center

   nova 服务状态异常
   
glance 服务
+++++++++++

.. figure:: /_static/images/glance_status.png
   :scale: 100
   :align: center

   glance 服务状态正常


消息队列服务状态
++++++++++++++++

在控制节点，使用如下的命令：

::

    rabbitmqctl status

.. figure:: /_static/images/rabbitmq_status.png
   :scale: 100
   :align: center

   rabbitmq 服务状态正常


Ceph集群状态
++++++++++++++++

在ceph集群上任意一个节点，使用ceph –s 命令：


.. figure:: /_static/images/ceph_status2.png
   :scale: 100
   :align: center

   rabbitmq 服务状态正常


异常服务重启
============

从上面的可以看到，nova服务、neutron服务异常，我们需要手动重启异常服务。

重启neutron服务
+++++++++++++++
-   首先在网络节点：

    ::

        cd /usr/bin/;
        for i in neutron*; do service $i restart; done;

-   然后在控制节点：

    ::

        cd /usr/bin/;
        for i in neutron*; do service $i restart; done;

-   然后检查状态:

    .. figure:: /_static/images/neutron_status2.png
       :scale: 100
       :align: center

    .. figure:: /_static/images/neutron_status3.png
       :scale: 100
       :align: center

    .. figure:: /_static/images/neutron_status4.png
       :scale: 100
       :align: center

    看最后一张图，neutron服务状态正常了。

重启nova服务
++++++++++++

#.  在控制节点

    ::

        cd /usr/bin;
        for i in nova*; do service $i restart; done

#.  然后在计算节点：

    ::

        cd /usr/bin;
        for i in nova*; do service $i restart; done

#.  检查服务：

    .. figure:: /_static/images/nova_status2.png
       :scale: 100
       :align: center

    .. figure:: /_static/images/nova_status3.png
       :scale: 100
       :align: center

    可以看到，nova服务状态也正常了。

启动虚拟机测试
==============

租户用户登录，然后创建虚拟机。使用cirros测试镜像。

.. figure:: /_static/images/lanch_instance_test1.png
   :scale: 100
   :align: center

.. figure:: /_static/images/lanch_instance_test2.png
   :scale: 100
   :align: center

.. figure:: /_static/images/lanch_instance_test3.png
   :scale: 100
   :align: center


从最后一张图可以看到，虚拟机创建成功。至此，云平台核心服务正常。


脚本
=====

另外，自己写了一个简单的脚本，检查OpenStack相关
核心组件的服务状态。该脚本基于Ubuntu部署的OpenStack！

.. literalinclude:: /_static/common/check_os_status.sh
   :language: bash
   :linenos:
