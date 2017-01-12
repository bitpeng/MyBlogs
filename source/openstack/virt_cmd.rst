.. _virt_cmd:


虚拟化相关命令
###############

.. contents:: 目录

------------------

virsh
=======

::

    # 列出已运行的虚机
    virsh list
    # 列出所有的虚拟机
    virsh list --all
    # 导出虚机对应的xml文件
    virsh dumpxml instance-00000037
    # 根据xml文件定义虚机
    ## 特别注意，通过define定义的虚机，会在 /etc/libvirt/qemu 目录下生成 instance-name.xml 文件
    virsh define demo.xml
    # 启动虚机
    virsh start test
    # 编辑虚机对应的xml文件；
    virsh edit test
    # 关闭虚机
    virsh shutdown test
    # 删除虚机
    virsh undefine test
    # 强制关机虚机
    virsh destroy test
    # 列出libvirt管理的秘钥
    virsh secret-list
    # 删除秘钥
    virsh secret-undefine <uudi>


qemu
=====

有关qemu磁盘加密的命令，可以参考另一篇文章：

