.. _centos_vm_netconfig:


########################
Centos虚拟机联网配置
########################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::
    在OpenStack云平台创建centos虚拟机，启动后发现无法上网。Google了一番之后，解决问题，于是记录下来，以作参考。

    版本：Centos6.5 版


.. contents:: 目录



--------------------------


问题排查
========================

查看网络配置
++++++++++++++


Centos虚拟机启动后，无法联网， Centos 的网络配置如下：

.. figure:: /_static/images/centos_vm_ifconfig.png
   :scale: 100
   :align: center

   Centos ifconfig


然后查看centos的网卡配置和网卡启动脚本配置, 可以看到，启动脚本里，只有ifcfg-eth0脚本；
而Centos虚拟机是从虚拟网卡(virtio-pci)联网的, 因此肯定网络不通。

.. figure:: /_static/images/centos_netrule_org.png
   :scale: 100
   :align: center

   Centos 网卡配置


.. figure:: /_static/images/centos_vm_ifcfg_pri.png
   :scale: 100
   :align: center

   Centos网卡启动脚本配置


增加虚拟网卡配置
++++++++++++++++

定位到原因后，剩下的问题就简单了，我们只需要增加虚拟网卡配置文件(ifcfg-eth1)，然后重启网络服务即可。

::

    DEVICE=eth1
    HWADDR=fa:16:3e:5f:ca:91
    TYPE=Ethernet
    ONBOOT=yes
    NM_CONTROLLED=yes
    BOOTPROTO=dhcp

.. important::
    特别注意：增加虚拟网卡配置文件，HWADDR的值要和/etc/udev/rules.d/70-persistent-net.rules文件中相应的
    硬件地址对应上。

重启网络服务：

::

    service network restart


.. figure:: /_static/images/centos_vm_ping_success.png
   :scale: 100
   :align: center

   增加虚拟网卡配置文件后，虚拟机之间成功互联



增加路由
========================

经过上面的步骤之后，发现OpenStack之间的虚拟机可以相互ping通，但是centos还是无法上网。
由于OpenStack里Windows虚拟机可以上网，因此初步猜想是由于路由引起的。


.. figure:: /_static/images/windows_vm_route.png
   :scale: 100
   :align: center

   windows虚拟机路由配置



.. figure:: /_static/images/centos_vm_route_pri.png
   :scale: 100
   :align: center

   Centos虚拟机路由配置


可以看到，windows有一条默认路由(目的地为0.0.0.0， 网关为10.10.10.10.1), 而10.10.10.1位虚拟路由器，
刚好是虚拟机流量出口网关，因此尝试在centos上也加一条默认路由。

::

    route add -net 0.0.0.0 gw 10.10.10.1


.. figure:: /_static/images/centos_vm_route_new.png
   :scale: 100
   :align: center

   增加路由，成功联网


.. tip::
    重启虚拟机之后，假如又无法联网了，这时只需重启网络服务并增加路由即可(不过经过上面的配置之后，一般
    重启之后都可以联网)，如下命令：

    ::

        service network restart
        route add -net 0.0.0.0 gw 10.10.10.1


---------------------

参考
=====

.. [#] http://www.jb51.net/os/RedHat/189963.html
.. [#] http://blog.chinaunix.net/uid-26495963-id-3230810.html
.. [#] http://os.51cto.com/art/201202/314888.htm
.. [#] http://my.oschina.net/xiaozhublog/blog/700327
.. [#] http://blog.csdn.net/kevinhwm/article/details/8987814

