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

虚机诊断信息
+++++++++++++

::

    source /smbshare/chensqrc
    nova list
    # 获取test虚机的诊断信息
    # 只有租户可以获取诊断信息
    nova diagnostics test


其他命令收集
============

::

    # 使用admin 身份
    source /root/openstackrc

    # 创建租户
    keystone tenant-create --name csq --description "csq tenant"
    # 创建租户用户
    keystone user-create --name demo2 --tenant csq --pass demo --email demo@cecgw.cn
    keystone user-role-add --user=demo2 --tenant=csq --role=system_tenant

    #keystone user-delete chensq

    # 创建外部网络
    neutron net-create ext-net --shared --router:external=True --provider:network_type vxlan --provider:segmentation_id 5000
    # 创建外网子网
    neutron subnet-create ext-net 192.168.159.0/24 --name ext-subnet --allocation-pool start=192.168.159.201,end=192.168.159.210 --gateway 192.168.159.2 --dns-nameserver 114.114.114.114

    source /smbshare/chenrc
    # 创建租户网络
    neutron net-create demo-net
    neutron subnet-create demo-net 10.10.10.0/24 --name demo-subnet --allocation-pool start=10.10.10.2,end=10.10.10.254 --gateway 10.10.10.1 --dns-nameserver 114.114.114.114
    # 创建路由，设置外网网关，内网接口！
    neutron router-create demo-router
    neutron router-gateway-set demo-router ext-net
    neutron router-interface-add demo-router demo-subnet

    #查看所有的虚机/某个租户虚机
    source /root/openstackrc
    nova list --all-tenants
    nova list --tenant csq

    # 迁移虚机，迁移虚机时使用虚机名称总是提示找不到名字。
    source /root/openstackrc
    nova migrate <server-id>


---------------------

参考
=====

.. [#] http://os.51cto.com/art/201404/435615.htm

