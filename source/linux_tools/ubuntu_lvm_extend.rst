.. _ubuntu_lvm_extend:


########################
Ubuntu根分区使用Lvm扩容
########################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. contents:: 目录

--------------------------

ubuntu 根分区剩余空间不足，影响工作，因此通过lvm工具对根文件系统进行扩容

.. note::

    系统版本：ubuntu-14.04 LTS


操作步骤
========

- 新建一块硬盘并进行分区：

  ::

    fdisk /dev/sde

  依次键入n, 创建新分区；然后分区类型选择p; 其他默认输入即可。

  .. figure:: /_static/images/ubuntu_lvm_1.png
     :scale: 100
     :align: center

     图1：创建新分区

  分区创建完成后，修改分区类型为lvm:

  .. figure:: /_static/images/ubuntu_lvm_2.png
     :scale: 100
     :align: center

     图2：修改分区类型

  .. note::

    新建的分区类型不能为扩展分区，否则不能更改分区类型，目前还不清楚原因，需要继续查找其他资料, 弄清原因。

    .. figure:: /_static/images/ubuntu_lvm_3.png
       :scale: 100
       :align: center

       图3：扩展分区修改类型失败

- 格式化分区：

  ::

    mkfs.ext4 /dev/sde1

- 创建新PV：

  ::

    pvcreate /dev/sde1

- 查看卷组信息，并扩展根系统所在卷组：

  .. figure:: /_static/images/lvm_vginfo.png
     :scale: 100
     :align: center

     图4：查看卷组信息

  .. figure:: /_static/images/lvm_extend_vg.png
     :scale: 100
     :align: center

     图5：扩展卷组


- 扩展根文件系统所在逻辑卷组；

  .. figure:: /_static/images/lvm_df_info.png
     :scale: 100
     :align: center

     图6：根文件系统信息

  .. figure:: /_static/images/lvm_extend_lv.png
     :scale: 100
     :align: center

     图7：扩展逻辑卷

- 使得扩容生效：

  .. figure:: /_static/images/resize2fs.png
     :scale: 100
     :align: center

     图8：执行扩容命令

  .. figure:: /_static/images/lvm_new_df_info.png
     :scale: 100
     :align: center

     图9：根文件系统可用空间已经增大


命令汇总
========

::

    fdisk /dev/sde
    partprobe
    fdisk  /dev/sde
    mkfs.ext4 /dev/sde1
    pvcreate /dev/sde1
    vgdisplay
    df -hl
    vgextend  ubuntu-vg /dev/sde1
    lvdisplay
    lvextend -L 37G /dev/mapper/ubuntu--vg-root
    resize2fs /dev/mapper/ubuntu--vg-root

