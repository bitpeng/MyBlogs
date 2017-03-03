.. _net_dev:


########################
网络各层设备简介
########################

**date: 2017-2-25 12:00**

.. contents:: 目录

--------------------------

`neutron无非就是将传统的物理硬件设备(如网线、网卡、服务器、交换机、路由器等)按照TCP/IP的四个层次架构
(数据链路层、网络层、传输层、应用层)，通过软件编程的方式，予以全部虚拟化、软件化和抽象化。` [1]_


鉴于此，我们先来了解下传统的TCP/IP网络架构各层设备及其功能、特点等。

得益于自己之前还算不错的TCP/IP网络基础知识(TCP/IP详解读了5+遍吧)，
有些东西虽然遗忘了点，但是看到相关概念或者阐述还是能很快回忆和理解！

下图是典型的OSI七层模型图：

.. figure:: /_static/images/osi_layer.png
   :scale: 100
   :align: center

   OSI七层模型


物理层
========

物理层发送的是bit串！

物理层对应的主要设备有：HUB，中继器，网线(如果也算的话)等。

- 中继器： 将信号放大再调整传输，防止网络早期远距离传输的信号衰减。
- HUB：HUB模式下，某主机A向连在同一个HUB的主机B发送bits时，是先将bits发给HUB，然后HUB直接发送给与该HUB相连接的每一个机器；
  HUB中若有有多个主机想发送bits，那么冲突可能会相当严重。因此后来引入了Ethernet HUB，它有一个所谓的CSMA/CD检测算法，
  用来解决HUB的冲突问题。**半双工传输！**


数据链路层
===========

主要功能是数据包分帧，物理寻址等。该层的主要设备有：

- 网卡：又称NIC卡，用于计算机和局域网的通信。
- L2-switch：交换机和HUB有一点相似，和计算机之间都使用双绞线连接，但是又有如下重要不同。

  * L2-switch全双工传输，可以同时收发数据；
  * 内置MAC学习机制，只把数据包发给和他相连接的目的设备；而HUB收到数据包会发给相连接的每一台设备；
  * 传输数据更快，性能更高；
- 网桥：用于在数据链路层扩展以太网，根据MAC帧的目的地址对收到的帧进行转发和过滤。
  含有转发表。它隔离了冲突域，但不隔离广播域。

  另外需要注意的是：bridge所连接的两个LAN需要使用的是同样的协议。并且birdge在每一划分子网的情况下，
  将物理网络分成两个相对独立网络。**网桥通过学习每个网络接口上的MAC层地址 (以太网地址) 工作。
  只当数据包的源地址和目标地址处于不同的网络时， 网桥才进行转发。**
  因此在很多方面，网桥就像一个带有很少端口的以太网交换机。


网络层
=========

主要功能是对IP数据包进行IP选路。

- 路由器：连接不同局域网，广域网，在不同网络间转发IP分组。
- L3-switch：具有路由功能的交换机。

其他网络设备
=============

gateway
++++++++

`Gateway is a device which is used to connect multiple networks and passes packets from one packet to the other network. Acting as the ‘gateway’ between different networking systems or computer programs, a gateway is a device which forms a link between them. It allows the computer programs, either on the same computer or on different computers to share information across the network through protocols. A router is also a gateway, since it interprets data from one network protocol to another.`

`Others such as bridge converts the data into different forms between two networking systems. Then a software application converts the data from one format into another. Gateway is a viable tool to translate the data format, although the data itself remains unchanged. Gateway might be installed in some other device to add its functionality into another.`

关于网关，上面的解释有点晦涩，实际上网关可以认为是起着协议转换的作用。举个简单例子：
我们在浏览网页时，有时可以在页面上看到FTP连接，然后我们点击FTP链接，就可以直接下载文件，
点击页面链接时发起的是HTTP请求，HTTP请求经过网关处理，转换成对FTP服务器的下载文件请求，文件下载完成后，
网关又把FTP文件当成HTTP报文内容，返回HTTP response。这样，我们就收到下载好的FTP文件了！
所以在这个例子中，网关转换我们的HTTP请求为FTP请求，并包装FTP文件返回HTTP响应。

Modems
++++++++

调制解调器，俗称猫。把计算机产生的数字信号转换成模拟信号，以便信号通过电话线传输！
在云计算网络中没有对应虚拟化设备，了解即可。

参考
=====

.. [1] 比较好的介绍了OpenStack网络虚拟化的基本原理。网址：http://www.openstack.cn/?p=4527
.. [#] 对TCP/IP架构各层网络设备有比较全面的介绍。网址：http://www.certiology.com/computing/computer-networking/network-devices.html
.. [#] freebsd手册，介绍了网桥的基本概念和相关命令和用法。\
       网址：https://www.freebsd.org/doc/zh_CN.UTF-8/books/handbook/network-bridging.html
.. [#] freebsd手册，介绍网络路由器。网址：https://www.freebsd.org/doc/zh_CN.UTF-8/books/handbook/network-routing.html
.. [#] 介绍了混杂模式，集线器，交换机等，非常清晰！网址：http://book.51cto.com/art/201202/316585.htm
