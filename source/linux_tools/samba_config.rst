Samba共享访问配置
##################


.. note::
    有时需要在在Windows和Linux之间传输文件，可以通过Samba共享实现。实例尝试
    在windows下访问Linux中文件，通过在Linux配置samba,smb用户名为smbuser1:123456.共享访问目录为/smbshare

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
