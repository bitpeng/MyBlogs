.. _lanch_instance_failure:


############################
OpenStack 启动虚拟机失败分析
############################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::
    在聚安云平台创建虚拟机失败。通过一番定位后，问题解决，于是记录下来，以作参考。

    版本：聚安云v2.5; OpenStack Juno版本

    出错：Ceph作为后端存储，镜像可以上传，但是无法启动虚拟机。


.. contents:: 目录



--------------------------


问题排查
==========



启动虚拟机时，选择启动方式，其中从 `镜像启动` 操作成功，但是选择 `从镜像启动(并创建一个新磁盘)` 方式启动失败.

.. figure:: /_static/images/select_lanch_type.png
   :scale: 100
   :align: center

   选择虚拟机启动源

选择 `从镜像启动(并创建一个新磁盘)` 方式启动失败, 出错信息如下：


.. figure:: /_static/images/lanch_instance_error.png
   :scale: 100
   :align: center

   创建虚拟机失败


根据出错Id \ ``90be2aa5-4187-44c7-94ca-567a5f7c822a``\ 查看日志

::

    cd /var/logs
    egrep "i90be2aa5-4187-44c7-94ca-567a5f7c822a" . -Rn

.. figure:: /_static/images/nova_log_error.png
   :scale: 100
   :align: center

   日志出错信息

查看相应日志文件:

.. figure:: /_static/images/Invalid_volume.png
   :scale: 100
   :align: center

   提示Invalid volume


由于镜像可以上传，但是无法创建volume，暂时判断是volume和ceph配置的问题。


Nova 绑定 Ceph rbd 块设备配置
===============================

.. important::
    为了绑定 Cinder 设备（块设备或者启动卷），必须告诉 Nova（和 libvirt）
    用户和 UUID。libvirt 在与 Ceph 集群进行连接和认证的时候提供这个用户。

    这两个配置项同样用于 Nova 的后端。

    ::

        rbd_user = cinder
        rbd_secret_uuid = `uuidgen`


.. figure:: /_static/images/rbd_secret_uuid.png
   :scale: 100
   :align: center

   查看 nova 和 cinder 的 rbd_secret_uuid配置, 果然不一样


至此，问题已经初步定位出来了，然后把nova.conf 和 cinder.conf 的rbd_secret_uuid改为一致，并重启服务.

::

    cd /usr/bin/
    for i in cinder*; do service $i restart;done
    for i in nova*; do service $i restart;done
    for i in glance*; do service $i restart;done


.. figure:: /_static/images/lance_instance_success.png
   :scale: 100
   :align: center

   成功创建虚拟机


---------------------

参考
=====

.. [#] http://my.oschina.net/JerryBaby/blog/376580#OSC_h3_10
.. [#] http://docs.ceph.org.cn/rbd/rbd-openstack/
.. [#] http://www.aichengxu.com/view/2501948
.. [#] http://docs.openfans.org/ceph/ceph4e2d658765876863/ceph-1/copy_of_ceph-block-device3010ceph57578bbe59073011/openstack301057578bbe59077684openstack3011#u
