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

    在公司有机会在Dell服务器上部署OS多次，现在把相关问题和知识点记录下来，作为参考。


.. contents:: 目录

-------------------

raid 基础知识
=============

raid 简介
++++++++++

.. figure:: /_static/images/why_raid.png
   :scale: 100
   :align: center


.. figure:: /_static/images/raid_howto.png
   :scale: 100
   :align: center
   

.. figure:: /_static/images/raid_obj.png
   :scale: 100
   :align: center

raid 关键技术
+++++++++++++

**RAID中有三项关键技术：分条、镜像和奇偶校验**

.. figure:: /_static/images/raid_stripe.png
   :scale: 100
   :align: center
   

.. figure:: /_static/images/raid_img.png
   :scale: 100
   :align: center
   

.. figure:: /_static/images/raid_check.png
   :scale: 100
   :align: center

   
.. figure:: /_static/images/raid_data_restore.png
   :scale: 100
   :align: center   

raid 常用级别
+++++++++++++

一共有0~6一共7种，这其中RAID0、RAID1、RAID5和RAID6比较常用。


.. figure:: /_static/images/raid_level.png
   :scale: 100
   :align: center  
   
   raid 常用级别

.. attribute:: RAID0

    如果你有n块磁盘，原来只能同时写一块磁盘，写满了再下一块，做了RAID 0之后，
    n块可以同时写，速度提升很快，但由于没有备份，可靠性很差。**n最少为2(自备注：在实践中，一块
    硬盘也可以制作raid0)。**
    
    .. figure:: /_static/images/raid0.png
       :scale: 100
       :align: center  

.. attribute:: RAID1

    正因为RAID 0太不可靠，所以衍生出了RAID 1。如果你有n块磁盘，把其中n/2
    块磁盘作为镜像磁盘，在往其中一块磁盘写入数据时，也同时往另一块写数据。
    坏了其中一块时，镜像磁盘自动顶上，可靠性最佳，但空间利用率太低。n最少为2。
    
    .. figure:: /_static/images/raid1.png
       :scale: 100
       :align: center  

.. attribute:: RAID3

    为了说明白RAID 5，先说RAID 3.RAID 3是若你有n块盘，其中1块盘作为校
    验盘，剩余n-1块盘相当于作RAID 0同时读写，当其中一块盘坏掉时，
    可以通过校验码还原出坏掉盘的原始数据。这个校验方式比较特别，奇偶检验，
    1 XOR 0 XOR 1=0，0 XOR 1 XOR 0=1，最后的数据时校验数据，
    当中间缺了一个数据时，可以通过其他盘的数据和校验数据推算出来。
    但是这有个问题，由于n-1块盘做了RAID 0，每一次读写都要牵动所有盘来为它服务，
    而且万一校验盘坏掉就完蛋了。最多允许坏一块盘。n最少为3.

    .. figure:: /_static/images/raid3.png
       :scale: 100
       :align: center  

.. attribute:: RAID5

    在RAID 3的基础上有所区别，同样是相当于是1块盘的大小作为校验盘，n-1
    块盘的大小作为数据盘，但校验码分布在各个磁盘中，不是单独的一块磁盘，
    也就是分布式校验盘，这样做好处多多。最多坏一块盘。n最少为3.

    .. figure:: /_static/images/raid5.png
       :scale: 100
       :align: center  

raid 比较
+++++++++

**raid 级别比较汇总**

.. figure:: /_static/images/raid_cmp1.jpg
   :scale: 100
   :align: center  
   
.. figure:: /_static/images/raid_cmp2.png
   :scale: 100
   :align: center  

+-------+--------+--------+----------+--------+--------+--------------+
| 级别  |最少磁盘|冗余磁盘|磁盘利用率|读取性能|写入性能|可靠性        |
+=======+========+========+==========+========+========+==============+
| raid0 |     1  | 0颗    | 100%     | 高     | 最高   | 无           |
+-------+--------+--------+----------+--------+--------+--------------+
| raid1 |     2  | n/2颗  | 50%      | 最高   | 最差   | 最高         |
+-------+--------+--------+----------+--------+--------+--------------+
| raid3 |     3  | 1颗    | (n-1)/n  | 良好   | 一般   |支持单硬盘故障|
+-------+--------+--------+----------+--------+--------+--------------+
| raid5 | 3      | 1颗    | (n-1)/n  | 良好   | 一般   |支持单硬盘故障|
+-------+--------+--------+----------+--------+--------+--------------+

有关更多信息，可以参考：

.. [#] http://www.linuxidc.com/Linux/2015-08/122191.htm
.. [#] https://www.zhihu.com/question/20131784

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

.. attribute:: rebuilding

	在一次操作中，发现进入bios查看硬盘状态时，其中一块硬盘状态变成 rebuilding。
	后来经咨询Dell技术支持工程师。发现由于raid具有数据镜像和数据校验机制，这个状态表示
	该硬盘在重建恢复数据。

	.. figure:: /_static/images/raid_rebuild.png
	   :scale: 100
	   :align: center
	   
	   硬盘重建恢复数据
	
	另外，在硬盘rebuilding时，硬盘所在的raid状态会提示为degraded，这是由于该raid某一块
	硬盘由于故障，正在进行重建恢复数据，数据raid级别会降级。当故障硬盘数据恢复后，raid
	状态会变成ready。
	
	.. figure:: /_static/images/raid_degraded.png
	   :scale: 100
	   :align: center
	   
	   raid重建故障恢复时级别降级

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
