##############
Linux命令
##############

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

性能调优
=========

释放缓存
++++++++

::

    echo 3 > /proc/sys/vm/drop_caches
