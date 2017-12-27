Samba共享访问配置
##################

.. contents:: 目录

-------------------

.. note::
    有时需要在在Windows和Linux之间传输文件，可以通过Samba共享实现。
    实例尝试在windows下访问Linux中文件，通过在Linux配置samba，
    smb用户名/密码为smbuser1:123456.共享访问目录为/smbshare

samba安装和配置
================

一. samba的安装

::

    sudo apt-get install samba


二. 创建共享目录

::

    mkdir /smbshare
    chmod 777 /smbshare –R


三. 创建Samba配置文件

1. 保存现有的配置文件

::

    sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak

2. 修改现配置文件

::

    sudo vi /etc/samba/smb.conf

在smb.conf最后添加

::

    security = user
    username map = /etc/samba/users

    [smbshare]
    path=/smbshare
    available=yes
    browseable=yes
    public=yes
    valid users = smbuser1
    writeable=yes


四. 创建samba帐户

::

    sudo touch /etc/samba/smbpasswd
    smbpasswd -a smbuser1

然后会要求你输入samba帐户的密码

.. note::

    - ps1：如果没有第四步，当你登录时会提示 ``session setup failed: NT_STATUS_LOGON_FAILURE``
    - ps2：如果提示 ``Failed to add entry for user`` ，则表示没有对应的用户。
      需要先增加一个系统用户smbuser1（增加一个和samba用户名一样的系统用户）。
      命令如下： ``useradd smbuser1``


五. 重启samba服务器

::

    sudo /etc/init.d/samba restart


六. 测试

::

    smbclient -L //localhost/share


七. 使用

可以到windows下输入ip使用了，在文件夹处输入 "\\" + "Ubuntu机器的ip或主机名" + "\\" + “smbshare”
提示输入认证时：用户名为smbuser1，密码为增加smb用户smbuser1时输入的密码。


自动化脚本
============


.. literalinclude:: /_static/src/src-samba_share.sh
   :language: bash
   :emphasize-lines: 12,15-18
   :linenos:

mount共享
==========


有时因为公司网络访问限制，不允许访问外网，那么samba无法安装，也就无法共享了。
此时可以退而求其次，通过mount命令，在windows宿主机和vmware中的Linux虚机进行文件共享！

- 首先，在windows宿主机中创建一个共享文件夹。设置方式为属性-共享-everyone读取/写入；
- 在Linux虚机中创建一个目录 mkdir /winshare
- 执行挂载命令：

  ::

      #mount -t cifs //<win-host-ip>/share /winshare -o username=<win-user-name>,rw
      mount -t cifs //10.11.113.75/share /winshare -o username=cec,rw

  其中share是windows共享文件夹，注意该文件夹要进行共享设置，最好不用密码进行操作！
  挂载后，将要共享的文件夹拷贝到该目录，则宿主机和虚拟机都可以进行查看！

需要注意如下几点：

* 如果挂载过程出现 ``mount: block device //xxx is write-protected, mounting read-only`` 错误，
  则需要安装cits组件。使用安装即可！

  ::

    apt-cache search cifs | grep -i cifs
    apt-get install cifs-utils

* **特别注意：挂载在Linux下的挂载目录，挂载成功后，目录下所有东西都将被清空！**
  这里cifs是一种网络文件系统！可以google获取相关知识。

.. note::

    更新：2017-09-19

    最近因为在某个场景，有挂载需求，结果怎么都挂载不上。google查找了很多资料，
    说可能是smb协议版本的问题，按照google结果，怎么操作都不可行。

    后来，和同事说起这个问题，他试了下，然后发现是windows防火墙的原因。因此，
    遇到类似网络问题，我们需要先检测端口是不是正常，由于cifs协议使用的是139和445端口，
    我们可以使用命令探测windows主机是不是开放了这些端口。

    .. code-block:: console

        root@ubuntu:/smbshare/clog# nc -v -w 1 10.11.111.47 -z 445
        nc: connect to 10.11.111.47 port 445 (tcp) failed: Connection refused
        root@ubuntu:/smbshare/clog#
        root@ubuntu:/smbshare/clog# nc -v -w 1 10.11.111.47 -z 139
        Connection to 10.11.111.47 139 port [tcp/netbios-ssn] succeeded!
        root@ubuntu:/smbshare/clog# nc -v -w 1 10.11.111.47 -z 1-1000

    假如发现端口没有开放，考虑关闭windows防火墙，再试一试上述命令

kvm宿主机和虚机文件共享
========================

之所以有这个需求，是由于某次大数据集群环境搭建中，通过在OpenStack云环境中，
开启多个虚机，然后安装spark等软件并配置。假如在虚机中依次安装spark等软件，那真的很费时间，
因此，可以通过制作一个qemu/kvm制作一个镜像，在镜像里面安装好spark等软件。然后，
利用该镜像启动的虚机，也是已经包含spark等软件的，我们只需要配置即可。

qemu/kvm制作镜像很容易，可是，要在镜像里面安装软件，却比较麻烦。kvm命令启动的虚机，并不能联网(或者，
怎么配置kvm虚机进行联网，我并不太熟悉。)，因此，只有通过宿主机往kvm虚机拷贝软件安装包。

这个问题我尝试了很久，最后通过google，找到了如下的解决办法。

::

    #在宿主机上执行
    kvm -m 1024 -redir tcp:3456::22 -drive file=centos-7.qcow2 -boot d -nographic -vnc :2

    #在客户机上执行，远程拷贝宿主机上的文件。
    scp user@hostip:/home/user/file .


.. [#] 关于在kvm虚机和宿主机之间文件共享的详细介绍。网址：http://mathslinux.org/?p=202
