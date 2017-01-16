.. _qemu_img_encry:


nova虚机加密总结
######################

.. contents:: 目录

---------------------

把最近对 qemu-img 加密虚机磁盘和高安云v2.5创建加密虚机的相关知识做下总结。


预备知识
=========

高安云v2.5基于 OpenStack Juno 版本，该版本可以在 nova/glance/cinder 中统一
用ceph做后端存储。

.. code-block:: console

    root@allinone-v2:/smbshare#  rados -p images ls
    rbd_data.10807612e851.0000000000000000
    rbd_data.10807612e851.0000000000000003
    rbd_directory
    rbd_data.10807612e851.0000000000000001
    rbd_header.10807612e851
    rbd_id.b5351923-136c-484a-a538-49f81bdf9497
    rbd_data.10807612e851.0000000000000002
    rbd_data.10807612e851.0000000000000004
    root@allinone-v2:/smbshare# for i in $(rados -p images ls | grep rbd_data); do rados -p images stat $i; done
    images/rbd_data.10807612e851.0000000000000000 mtime 1480335467, size 8388608
    images/rbd_data.10807612e851.0000000000000003 mtime 1480335471, size 8388608
    images/rbd_data.10807612e851.0000000000000001 mtime 1480335468, size 8388608
    images/rbd_data.10807612e851.0000000000000002 mtime 1480335470, size 8388608
    images/rbd_data.10807612e851.0000000000000004 mtime 1480335472, size 7571968


.. code-block:: console

    root@allinone-v2:/smbshare# source /root/openstackrc
    root@allinone-v2:/smbshare# glance image-list
    +--------------------------------------+---------------+-------------+------------------+----------+--------+
    | ID                                   | Name          | Disk Format | Container Format | Size     | Status |
    +--------------------------------------+---------------+-------------+------------------+----------+--------+
    | b5351923-136c-484a-a538-49f81bdf9497 | cirros-x86_64 | raw         | ovf              | 41126400 | active |
    +--------------------------------------+---------------+-------------+------------------+----------+--------+
    root@allinone-v2:/smbshare# glance image-show cirros-x86_64
    +------------------+--------------------------------------+
    | Property         | Value                                |
    +------------------+--------------------------------------+
    | checksum         | 0590d15336f919496ccc91b2c0f667bc     |
    | container_format | ovf                                  |
    | created_at       | 2016-11-28T12:17:45                  |
    | deleted          | False                                |
    | disk_format      | raw                                  |
    | id               | b5351923-136c-484a-a538-49f81bdf9497 |
    | is_public        | True                                 |
    | min_disk         | 0                                    |
    | min_ram          | 0                                    |
    | name             | cirros-x86_64                        |
    | owner            | fd616fcac0724cbea065a786bab4587e     |
    | protected        | False                                |
    | size             | 41126400                             |
    | status           | active                               |
    | updated_at       | 2016-11-28T12:18:00                  |
    +------------------+--------------------------------------+

我们只上传了一个镜像到glance，刚好上传的镜像大小与 images/rdb_data.10807612e851 之和相等。

通过 horizon 启动虚机时，可选择不同的启动项包括："从镜像启动"，"从镜像启动(创建新硬盘)" 等；
通过代码分析可知选择不同的启动项时，最终会在 self.driver.spawn() 中通过不同
的 image_backend 获取镜像。其中"从镜像启动"时
imaeg_backend 为 ``nova.virt.libvirt.imagebackend.Qcow2``，其他启动方式对应的 image_backend
是 Rbd 或者 Raw，而只有qcow2格式的虚拟磁盘才支持加密。因此，只有"从镜像启动"时才可以设置虚机
加密，为了方便讨论，下面我们都假设是"从镜像启动"，镜像为cirros-x86_64 启动虚机。

openstack libvirt启动虚机时，磁盘镜像的主要传输过程如下图所示：

.. figure:: /_static/images/disk_image.png
   :scale: 100
   :align: center

nova/virt/libvirt/LibvirtDriver:_create_image() 函数会尝试从 glance 获取cirros镜像，并缓存在
本地 /var/lib/nova/instances/_base 目录里，然后通过 qemu-img create -o backing_file 命令，
在虚机目录下生成 disk 磁盘文件。

.. code-block:: console

    root@allinone-v2:/var/lib/nova/instances# tree
    .
    ├── aa8e9ed7-ca99-43c0-9d71-c5ae0e98a746
    │   ├── console.log
    │   ├── disk
    │   ├── disk.info
    │   └── libvirt.xml
    ├── _base
    │   └── 6a6f72f6c315b082cba3e32e0ece4a5e933a868a
    ├── compute_nodes
    ├── f5f898c0-6206-4071-aa9f-3beb905f48e3
    │   ├── console.log
    │   ├── disk
    │   ├── disk.info
    │   ├── libvirt.xml
    │   └── secret.xml
    └── locks
        ├── nova-6a6f72f6c315b082cba3e32e0ece4a5e933a868a
        └── nova-storage-registry-lock

    4 directories, 13 files
    ## 从这里可以看出，base目录缓存的是从glance下载下来的 cirros 镜像。
    root@allinone-v2:/var/lib/nova/instances# qemu-img info _base/6a6f72f6c315b082cba3e32e0ece4a5e933a868a
    image: _base/6a6f72f6c315b082cba3e32e0ece4a5e933a868a
    file format: raw
    virtual size: 39M (41126400 bytes)
    disk size: 39M
    ## 通过 -o encryption 和 backing_file 选项，生成加密磁盘。
    root@allinone-v2:/var/lib/nova/instances# qemu-img info f5f898c0-6206-4071-aa9f-3beb905f48e3/disk
    image: f5f898c0-6206-4071-aa9f-3beb905f48e3/disk
    file format: qcow2
    virtual size: 1.0G (1073741824 bytes)
    disk size: 1.5M
    encrypted: yes
    cluster_size: 65536
    backing file: /var/lib/nova/instances/_base/6a6f72f6c315b082cba3e32e0ece4a5e933a868a
    Format specific information:
        compat: 1.1
        lazy refcounts: false

通过打log，可以看到生成加密磁盘执行的命令：

.. figure:: /_static/images/qemu_create_encry_disk.png
   :scale: 100
   :align: center

   生成加密磁盘命令

至此，虚机创建/虚机加密的整个流程就很清晰了。无非是调用qemu-img命令，根据虚机镜像
生成虚拟磁盘文件，然后通过libvirt API定义虚机xml文件并控制虚机的启动，运行，迁移等。

qemu-img 磁盘加密
==================

nova 创建虚机是借助于 libvirt--> qemu 来实现的。为此，我进一步试验了 qemu-img 有关磁盘
加密的命令，不同的加密选项差别很大。

backing_file
+++++++++++++

qcow 是 ``Qemu Copy On Write`` 的缩写。关于cow技术，可以自行搜索相关材料。

qemu 创建虚机磁盘时，通过 ``-o backing_file=file`` 或者 ``-b file`` 开启
写时复制。这样多个虚机磁盘，可以共享同一个 backfile ，并把自己独有的内容
写到自己的磁盘中。

**backfile 有一个重要特性，它是只读的。除非显示使用 commit 命令，将改动提交
到backfile。**

创建加密磁盘，开启backfile选项
+++++++++++++++++++++++++++++++

.. code-block:: console

    root@allinone-v2:/smbshare# qemu-img create -f qcow2 -o  backing_file=/var/lib/nova/instances/_base/6a6f72f6c315b082cba3e32e0ece4a5e933a868a,encryption=on,size=1073741824 /smbshare/encry3.qcow2
    Formatting '/smbshare/encry3.qcow2', fmt=qcow2 size=1073741824 backing_file='/var/lib/nova/instances/_base/6a6f72f6c315b082cba3e32e0ece4a5e933a868a' encryption=on cluster_size=65536 lazy_refcounts=off

经测试，使用这种方式加密的虚机，使用 ``virsh secret-list`` 中任意的的uuid，都可以正常启动虚机。

利用convert命令创建加密磁盘
++++++++++++++++++++++++++++

.. code-block:: console

    ## 该方式会提示输入密码，假设输入密码123456
    root@allinone-v2:/smbshare# qemu-img convert -f raw -O qcow2 -o encryption=on,size=1073741824 /var/lib/nova/instances/_base/6a6f72f6c315b082cba3e32e0ece4a5e933a868a encry2.qcow2
    Disk image 'encry2.qcow2' is encrypted.
    password:

这种方式加密的磁盘会提示输入秘钥，然后通过 virsh start 命令启动虚机时，只有 xml 文件中的 encryption 字段
uuid 为根据密码生成的才可以启动。

区别分析
+++++++++

一种提示输入密码，一种无需密码；一种用任意的 secret-uuid 都可以启动，另一种只有密码对应的 secret-uuid 才可以启动。
为何会表现出这么大的差别呢？

对此，我的理解是：

- 开启backfile选项时，backfile中是cirros镜像，而它并没有被加密；加密的是写时复制文件
  encry3.qcow2。相当于只加密了虚拟硬盘，而操作系统启动镜像并没有被加密。因此，只要是
  libvirt 中合法的 secret-uuid，都可以正常启动虚机。
- convert命令创建的磁盘，会将backfile和虚拟磁盘文件进行合并，encry2.qcow2 虚拟磁盘中，不仅仅有普通文件内容，还有cirros系统镜像，
  因此生成加密磁盘时，系统启动镜像也被加密掉了。因此只有正确的密码对应的 secret-uuid，才可以启动虚机。

待验证我的想法，初步的验证思路是创建一个加密的 cirros 镜像，然后利用该镜像再重复上述两步骤。

附录：实验步骤
===============

#. 导出某个虚机的xml文件

   ::

       virsh list --all
       # 导出虚机对应的 xml 文件
       virsh dumpxml instance-00000040 > /smbshare/encry2.xml

#. 编辑虚机xml文件，更改 name，将disk文件替换成 encry2.qcow2
#. 生成两个 secret-uuid，一个是随机的，一个是根据加密密码生成的。

   .. code-block:: shell

       cat << EOF >secret.xml
       <secret ephemeral='no' private='yes'>
       </secret>
       EOF

       secret_uuid=$(virsh secret-define secret.xml | awk '{print $2}')
       virsh secret-set-value $secret_uuid $(printf %s "123456" | base64)

#. 在 xml 配置文件磁盘段中添加秘钥：

   ::

       <encryption format='qcow'>
           <secret type='passphrase' uuid='3f8475e9-868c-4543-a510-7f668ba83d46'/>
       </encryption>

#. 定义虚机并启动：

   ::

       virsh define encry2.xml
       virsh start encry2

#. 利用 vncviewer 查看虚机是否正常启动(假如xml文件中定义了console.log 文件，观察该文件也可以)；
   然后依次利用不同的uuid和encry3.qcow2 重复上面的实验。

   ::

       virsh destroy encry2
       virsh undefine encry2
       virsh define encry2.xml


.. note::

    在 virsh define 虚机xml文件之前，生成 secret-uuid 并在 xml 文件中添加 encryption 字段的步骤
    必不可少，否则会 virsh 相关命令会提示磁盘已被加密错误。
