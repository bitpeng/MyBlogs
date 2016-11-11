.. _l_os_cmd:


########################
openstack命令汇总
########################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::
    - openstack 操作命令总结。

    - openstack启动后，注意要重点检查nova，neutron，ceph等服务状态是否正常。



.. contents:: 目录



--------------------------


neutron 相关
============

检查状态
++++++++

::

    neutron agent-list


.. figure:: /_static/images/check_neutron_status.png
   :scale: 100
   :align: center

   neutron 正常状态

查看网络列表：

::

    neutron net-list


nova 相关
============

检查状态
++++++++

::

    nova-manage service list|sort
    # 或者使用
    nova service-list

.. figure:: /_static/images/check_nova_status.png
   :scale: 100
   :align: center

   nova 正常状态


命令行新建虚拟机
++++++++++++++++

::

    nova --debug boot csq_test --flavor m1.tiny --image "dec2596b-1b1f-4eec-9cd9-b72fc8dc6f95" --security-groups default --nic net-id=1283f65b-2adc-4654-9cbe-0d0566bb0c1e

其中 flavor、security-groups、net-id分别使用下面命令可以获取：

::

	nova flavor-list
	nova secgroup-list
	glance image-list
	neutron net-list
	
命令行启动虚拟机
++++++++++++++++

::

	nova start/stop vm_id

---------------------

参考
=====

.. [#] http://os.51cto.com/art/201404/435615.htm

