################
Linux命令和shell
################

.. contents:: 目录

-------------------


get
======

下载整个网站
+++++++++++++

下载网站的整个目录，以供离线浏览

.. code:: shell

    wget -c -r -np -k -L -p http://docs.ceph.org.cn


nc
====

传输目录
++++++++

server端：

::

    tar -cvf - allinone-v2.5-install-script | nc -l 12345

client端：

::

    nc -n 192.168.159.146 12345 | tar -xvf -

传输文件
++++++++

server端：

::

    nc -l 12345 < file.txt


client端：

::

    nc -n 172.31.100.7 1567 > file.txt

然后两端分别使用md5sum命令核对文件传输是否出错.

scp
===

- 远程拷贝文件

  ::

      scp root@10.11.113.198:/smbshare/win7.raw .

- 远程拷贝目录

  ::

      scp -r root@10.11.113.198:/smbshare/ .


cut
====

::

    echo "test/dev/mapper/juno" | cut -d '/' -f1
    #test
    echo "test/dev/mapper/juno" | cut -d '/' -f2
    #dev
    echo "test/dev/mapper/juno" | cut -d '/' -f2-
    #dev/mapper/juno
    echo "/dev/mapper/juno" | cut -d '/' -f1
    #
    echo "/dev/mapper/juno" | cut -d '/' -f2
    #dev

.. [#] http://www.jb51.net/article/41872.htm


性能调优
=========

释放缓存
++++++++

::

    echo 3 > /proc/sys/vm/drop_caches

查看内存使用
++++++++++++++++

::

    free -hl




apt-get
=======
只获取包，不安装：

apt-get -d install git
apt-get -d install git --reinstall


route
========

添加路由：
route add -net 224.0.0.0 netmask 240.0.0.0 dev eth0


删除路由：

route del -net 224.0.0.0 netmask 240.0.0.0
route del -net 224.0.0.0 netmask 240.0.0.0 reject


awk
====

::

# 打印某一行, 自设定分隔符
awk -F: '{print $1}'
# 打印除第一行之外的所有行
awk '{$1="";print $0}'
# 循环把前N列都赋值为空，从第n+1列开始打印所有的列！
awk '{ for(i=1; i<=n; i++){ $i="" }; print $0 }' urfile

