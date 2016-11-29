.. _centos_net_sum:


########################
Centos 联网问题汇总
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::

	发现centos联网支持及配置没有ubuntu友好，当然也可能是不熟悉
	centos的原因。之前已经写过一篇 openstack centos实例联网配置的问题，
	这里，再把自己遇到的centos网络问题坐下总结！


.. contents:: 目录

--------------------------


centos VMware复制后无法上网
============================


vmware支持虚拟机复制功能，这样能极大的方便我们的使用。
可是自己复制一台centos虚拟机后，发现无法联网(ubuntu虚拟机
复制启动后，不用配置是可以直接联网的。)，可以使用如下方法解决：


::

	# 查看设备的硬件地址
	ifconfig -a
	# 将这两个文件中的硬件地址对应上，然后重启机器就可以。
	vi /etc/sysconfig/network-scripts/ifcfg-eht0
	vi /etc/udev/rules.d/70-persistent-net.rules

	
openstack centos镜像自动获取IP    
===============================

原来自己制作的openstack centos镜像，开启虚拟机实例后，都无法自动获取IP地址，
需要手动配置，非常麻烦。可以在镜像模板中，进行如下配置，亲测有效.

首先，编辑 /etc/sysconfig/network-scripts/ifcfg-eth0文件如下所示：

::

	DEVICE="eth0"
	BOOTPROTO=dhcp
	NM_CONTROLLED="yes"
	ONBOOT="yes"


然后，清除 /etc/udev/rules.d文件的网络设备命名规则，因为这些规则将从实例的网卡获得。
sudo rm -rf /etc/udev/rules.d/70-persistent-net.rules


