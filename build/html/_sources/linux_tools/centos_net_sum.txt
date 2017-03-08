.. _centos_net_sum:


########################
Linux 联网问题汇总
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
	这里，再把自己遇到的centos网络问题以及有关linux发行版联网问题作下总结！


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


VMware 联网问题
=================

在vmware安装好openstack juno，使用ceph作为统一后端存储，可以
正常上传镜像，可以正常启动虚拟机，但是却无法连接互联网。
由于在vmware中安装了其他的虚拟机，都可以联网，因此初步猜测，
可能是路由的问题！

正常可以联网的虚拟机route信息！

::

	# 正常可以联网的虚拟机route信息！
	root@ubuntu:~# route
	Kernel IP routing table
	Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
	default         192.168.159.2   0.0.0.0         UG    0      0        0 br-ex
	20.20.20.0      *               255.255.255.0   U     0      0        0 eth2
	101.101.101.0   *               255.255.255.0   U     0      0        0 eth1
	192.168.159.0   *               255.255.255.0   U     0      0        0 br-ex

以下是无法联网的虚机路由信息：

::

	# 无法联网的虚拟机路由信息
	root@ubuntu:/smbshare# route
	Kernel IP routing table
	Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
	default         192.168.159.1   0.0.0.0         UG    0      0        0 br-ex
	10.10.10.0      *               255.255.255.0   U     0      0        0 eth1
	20.20.20.0      *               255.255.255.0   U     0      0        0 eth2
	192.168.159.0   *               255.255.255.0   U     0      0        0 br-ex

果然，路由网关不一样，由于可以联网的虚拟机IP地址是DHCP方式的，而OpenStack juno
使用的是静态地址！因此，只需要:

::

	vi /etc/network/interfaces
	auto br-ex
	iface br-ex inet static
		address 192.168.159.155
		gateway 192.168.159.2
		netmask 255.255.255.0
		dns-nameservers 8.8.8.8

把网关改成 192.168.159.2即可！

ubuntu无法联网
===============

今天安装好ubuntu系统后，总是无法联网，重启多次都不行。

后来查看/etc/network/interfaces文件，发现只有lo设备配置。
因此在该文件最后两行加上eth0自动获取IP即可！

::

    auto eth0
    iface eth0 inet dhcp
