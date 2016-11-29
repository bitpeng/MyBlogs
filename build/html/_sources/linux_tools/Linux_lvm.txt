.. _Linux_lvm:


########################
Linux逻辑卷和lvm
########################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. note::
    Logical Volume Manager (LVM)，逻辑卷管理LVM是一个多才多艺的硬盘系统工具，
    无论在Linux或者其他类似的系统，都是非常的好用。传统分区使用固定大小分区，
    重新调整大小十分麻烦，但是LVM可以创建和管理“逻辑”卷，而不是直接使用物理硬盘，
    可以让管理员弹性的管理逻辑卷的扩大缩小，操作简单，而不损坏已存储的数据。
    可以随意将新的硬盘添加到LVM，以直接扩展已经存在的逻辑卷，LVM并不需要重启就可以
    让内核知道分区的存在。文章详细记录在PV/VG/LV中3个阶段的创建/添加/扩展/减小/删除
    等实战操作步骤，方便自己回顾一些基础用法，也希望能够帮助大家更好的理解LVM的原理。

    .. note::
        简言之：LVM是一个非常给力的工具，用来创建和管理可变大小的分区



.. contents:: 目录



--------------------------


Lvm 介绍
========================

分区管理
++++++++





::

    df -h
    fdisk /dev/sda
    n
    e
    3
    n
    p
    4
    w


.. tip::
    不知道为什么，新建分区时，先使用p命令建立主分区不可以，要先使用e命令，
    然后在使用p命令，才可以。







.. figure:: /_static/images/centos_vm_ifconfig.png
   :scale: 100
   :align: center

   Centos ifconfig



---------------------

参考
=====

.. [#] http://ju.outofmemory.cn/entry/244598
.. [#] https://lzw.me/a/linux-lvm.html
.. [#] https://wsgzao.github.io/post/lvm/
.. [#] https://linux.cn/article-3218-1.html
.. [#] https://wsgzao.github.io/post/lvm/
.. [#] https://linux.cn/article-3218-1.html
.. [#] http://dreamfire.blog.51cto.com/418026/1084729
.. [#] http://www.cnblogs.com/chengxuyuancc/articles/3433824.html
.. [#] https://www.ibm.com/developerworks/cn/linux/l-lvm2/
.. [#] http://ju.outofmemory.cn/entry/244598
.. [#] http://www.chinaunix.net/old_jh/4/258443.html
.. [#] https://lzw.me/a/linux-lvm.html
