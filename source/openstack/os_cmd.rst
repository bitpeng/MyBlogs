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

---------------------

参考
=====

.. [#] http://www.jb51.net/os/RedHat/189963.html

