.. _qemu_kvm:


qemu/kvm学习笔记
#################


.. contents:: 目录

------------------

最近分析 nova 组件以及启动虚机流程，已经看到通过 driver spawn虚机部分了。
由于没有虚拟化方面的基础，代码看的很费劲，因此停留下来，补了补虚拟化方面
的知识，自己通过 google 搜索阅读了很多的讲解，中英文的都有。现在在自己理解
的基础上，写一篇总结笔记。


虚拟化
========

虚拟化类型从不同分类角度来说包括软件虚拟化、硬件辅助虚拟化、半虚拟化、全虚拟化等：

- 软件虚拟化，解析 guest os 所有指令并仿真处理；
- 硬件辅助虚拟化，需要 CPU 支持虚拟化，然后对于 guest os 的特权指令，通过 trap 捕获并处理；
- 半虚拟化，对 guest os 的特权指令进行修改；
- 全虚拟化，guest os 不需要任何的修改；

另外，根据 Hypervisor 是直接管理裸机还是部署于os之上，又可以分为I型/II型虚拟化。
I型虚拟化直接部署于裸机，如 xen；II型虚拟化部署于宿主机os之上，如 vmware workstations。


kvm 
====

KVM 是基于 X86 CPU 硬件辅助虚拟化支持的Linux平台原生的全虚拟化解决方案。
kvm 是 linux 内核的模块，它实现了对 CPU 和内存的模拟，可以通过如下命令，
判断是否系统是否支持或者开启 CPU 虚拟化以及内核是否已经加载 kvm 模块:

::

    # vmx for intel and svm for amd
    grep -P "vmx|svm" /proc/cpuinfo
    
    lsmod | grep kvm

在 kvm 虚拟化解决方案中，
虚拟机是 Linux 的一个 kvm进程，每个 vcpu 都对应一个线程，如下图:

.. figure:: /_static/images/kvm_model.png
   :scale: 100
   :align: center

   KVM虚拟化模型
   

OpenStack 通过 libvirt 启动的虚机，不过是 qemu_system_x86_64 开启 kvm 加速的一个进程：

::

    ps -ef | grep -P "kvm|qemu-"

.. figure:: /_static/images/qemu_system_x86_64.png
   :scale: 100
   :align: center

   虚机对应 qemu 进程
   
qemu-kvm
=========

kvm 实现了 CPU 和内存的虚拟化，而这是远远不够的。对于外部设备的模拟，社区
选择了qemu。

qemu是纯软件实现的全套虚拟化解决方案，仿真处理 guest os 的指令，效率
比较低。后来社区 fork 分支 qemu-kvm，把 CPU 和内存的替换成 kvm，而设备的
模拟代码部分保留下来，从而实现虚拟化加速、提高性能。并在1.3版本之后合并
进主干分支，因此 qemu + kvm 就组成了一个完整的虚拟化平台。

.. code-block:: console

    root@allinone-v2:/# kvm-ok 
    INFO: /dev/kvm exists
    KVM acceleration can be used

在 :ref:`虚拟机镜像制作<image-guide>` 中，都是用 kvm 命令启动虚机并安装，
该命令需要安装 qemu-kvm 包：

.. code-block:: console

    root@allinone-v2:/# kvm
    The program 'kvm' is currently not installed. You can install it by typing:
    apt-get install qemu-kvm

安装好 qemu-kvm 包后，可以发现，``kvm`` 命令不过是 qemu 命令开启 kvm 加速的包装而已：

.. code-block:: console

    root@juno-controller:/smbshare# which kvm
    /usr/bin/kvm
    root@juno-controller:/smbshare# more $(which kvm)
    #!/bin/sh
    exec qemu-system-x86_64 -enable-kvm "$@"


qemu-img
=========

qemu-img 是 qemu 的虚拟磁盘管理命令。

镜像是包含可启动操作系统的虚拟磁盘文件。要制作镜像，我们需要一个虚拟磁盘，
这个虚拟磁盘就相当于物理机的硬盘，它用于安装虚拟机操作系统，虚拟磁盘有多
种不同的格式，常见的格式有 raw,qcow2,vmdk,vdi 等，raw格式是最常见的，随便创
建一个文件，或者使用dd生成一个文件，都是raw格式。

安装系统，有多种方法，但是基本的原理是一样的，一个虚拟磁盘，还需要一个ISO安装
文件，然后设置虚拟机从光盘启动，安装系统到虚拟磁盘上。通过以上步骤，我们就得到
一个操作系统镜像了。

根据上面的阐述，很容易理解，在 :ref:`虚拟机镜像制作<image-guide>` 中，制作镜像
的相关步骤和命令。

::

    # 制作空虚拟硬盘，由于安装centos
    qemu-img create -f raw centos-6.5.raw 10G
    # 开始安装，设置从虚拟光驱启动安装
    kvm -m 512 -cdrom CentOS-6.5-x86_64-bin-DVD1.iso -drive file=centos-6.5.raw -boot d -nographic -vnc :2
    # 安装完成，从硬盘自启动操作系统
    kvm -m 512 -drive file=centos-6.5.raw -boot c -nographic -vnc :2