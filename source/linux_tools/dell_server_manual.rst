.. _dell_server_manual:


########################
DELL 服务器操作手册
########################

..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. note::

    在公司有机会在Dell服务器上部署OS上多次，现在把相关问题和知识点记录下来，作为参考。


.. contents:: 目录

-------------------


磁盘与raid管理
==============

硬盘状态
+++++++++

在安装系统之前，我们首先需要进行raid配置。raid配置涉及到硬盘的一些状态，主要包括如下几种：

.. attribute:: failed

	硬盘状态错误，此时需要重启服务器，让系统对raid卡进行自检管理，一般重启后failed状态的硬盘会变成ready；

.. attribute:: foreign

	此时需要执行clear foreign disk。清除完成后，一般硬盘状态会变成ready;
	
.. attribute:: ready

	硬盘状态正常。此时需要通过新建virtual disk，硬盘才可以使用；
	
.. attribute:: online

	进行raid配置后正常的硬盘状态，此时硬盘可以被操作系统识别，或者进行系统安装等；


raid 配置
+++++++++

一般进行raid配置前(create new virtual disk), 需要清除之前的raid配置信息。

.. important::

	清除之前已有raid配置信息，并不会清除磁盘里面的用户数据。我们可以在原有的硬盘上，
	创建同样的raid配置信息，来恢复硬盘数据。(来自于dell官网)

	.. figure:: /_static/images/clear_raid_config.png
	   :scale: 100
	   :align: center

	   清除raid配置信息，该步骤不会清除硬盘数据


清除原有raid配置信息后，可以创建同样的磁盘阵列。只要没有做初始化，用户数据是存在的。
例如，服务器原先安装的Ubuntu操作系统还保存在硬盘上，马上我们就可以重启服务器，进入操作系统。


raid初始化
++++++++++

如果我们创建RAID阵列的目的是新部署一台服务器，我们建议所有新创建的RAID
阵列都应该做初始化操作。对raid执行初始化操作可以认为是普通硬盘的格式化操作，
raid硬盘上原有的用户数据将被清除。

.. note::

	对于Dell服务器而言，raid阵列建好后，可以执行完全初始化(start init)和快速初始化(fast init)。
	完全初始化比较慢，一般1T的硬盘完全初始化需要1个半小时。执行快速初始化既可！

	.. figure:: /_static/images/raid_init.png
	   :scale: 100
	   :align: center

	   raid阵列初始化操作，该步骤会清除硬盘所有用户数据。


Life Controller
===============

有时我们无法成功安装OS，这时可以通过生命控制器进行安装。life controller具有很多功能，
可以进行系统部署，raid 制作，硬件检测，系统日志等诸多操作。

.. figure:: /_static/images/life_controller.png
   :scale: 100
   :align: center

   生命周期控制器
   
.. tip::

	通过生命周期控制器部署系统，需要注意如下事项(Dell售后技术支持提供)：
	
	- boot mode只能选择bios，不能选UEFI；
	- 只支持通过USB光驱进行系统安装，不支持U盘安装；
	- 通过该方式部署，最好事先和服务器厂商确认所支持的操作系统。例如：dell h730 mini 
	  型号设备所支持的ubuntu系列仅仅为ubuntu-14.04.1;

.. error::

	假如系统重启后Life  Controller不可用，如提示Life Controller update required等。
	这时可以尝试按住开机按钮旁边的i键20秒，然后<ctrl + alt + del>重启机器，一般就可以使用F10进入
	Life Controller了。(Dell 技术支持提供，亲测有效。)

  
Boot Mode
=========

Dell系列服务器支持bios 和 UEFI启动模式。关于这两种启动模式的更多细节，可以自己网上
搜索相关材料。

.. figure:: /_static/images/boot_mode.png
   :scale: 100
   :align: center

   Boot Mode，在system bios里设置。
   
.. note::

	特别需要注意的是，假如设置boot mode为UEFI，这时系统启动后，将跳过
	raid自检，所以启动速度比较快。但是，这种方式也会造成用户无法通过
	<ctrl + R>进入Bios Configuration Utility。也就无法执行raid初始化
	等操作。
 

---------

参考
=====

.. [#] http://zh.community.dell.com/techcenter/systems-management/w/wiki/390.raid
.. [#] http://zh.community.dell.com/techcenter/systems-management/w/wiki/388.percraid
.. [#] http://www.cqeis.com/news_detail/newsId=1654.html
.. [#] http://zh.community.dell.com/techcenter/w/techcenter_wiki/190.poweredgelifecycle-controller
