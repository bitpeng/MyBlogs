###################
openstack 实践指南
###################

.. tip::

    利用部门服务器，自己准备搭建OpenStack来熟悉OpenStack的部署，运维等方面的知识；

    硬件： Dell e14s(PowerEdge R720)

.. contents:: 目录

--------------


准备工作
=========

raid 管理
+++++++++++


- v2.3版本lvm作存储，raid1一块(操作系统安装盘)，其他的作raid5；
- v2.5 ceph作存储，raid1一块，其他的raid0, 因为ceph本身有备份机制，不需要raid5；



安装Ubuntu Server
++++++++++++++++++

制作为U盘引导盘后，启动服务器，按f8，然后设置system bios，选择启动方式 UEFI 模式
保存重启，然后开始安装。



allinone方式部署
=================

.. note::
    下面以v2.5版本的juno install allinone脚本为例，说明部署方法和需要注意的细节.


安装allinone
+++++++++++++

在allinone安装脚本中，只需要配置setup.conf文件，分别设置外网、内网、管理网络的IP地址，掩码和网关即可。
然后执行setup.sh脚本。

::

    setup.sh




安装ceph
+++++++++

以下以ceph allinone脚本为例说明安装过程:

- 配置文件preconf;
- ceph 安装：
  ::

    ./ceph_install.sh

- ceph 初始化：
  ::

    ./ceph_initial.sh
- ceph 验证：
  ::

    ceph -s

  .. figure:: /_static/images/ceph_status.png

      图：ceph状态验证

- 创建pool和认证：
  ::

    ./create_pool.sh
    ./auth_user.sh


.. tip::
    -  ceph集群通信尽量使用内部网络IP，不要用外网ip；
    -  特别注意的是，由于ceph作为glance和cinder的后端存储，因此创建pool和认证必不可少，否则上传镜像肯定发生错误；
    -  v2.5 镜像格式只能使用raw格式，因为ceph作后端存储, 不支持qcow2格式;


镜像制作
+++++++++

OpenStack镜像制作，可以花一篇专门的笔记来介绍，请参考 :ref:`OpenStack镜像制作 <image-guide>`

.. important::
    v2.5 镜像格式只能使用raw格式，因为ceph作后端存储, 不支持qcow2格式;



OpenStack创建虚拟机
====================


nova设置secret
+++++++++++++++

.. important::
    OpenStack用户租户创建虚拟机，计算节点一定要设置secret，否则租户创建虚拟机时肯定不会成功。
    可以使用以下的脚本来设置secret。

.. literalinclude:: /_static/src/nova-set-secret.sh
   :language: sh
   :linenos:















--------------


参考
=================

.. [#] http://www.lai18.com/content/1477262.html
.. [#] 网际云安全套件v2.5 安装说明
