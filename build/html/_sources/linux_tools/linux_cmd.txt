################
Linux命令和shell
################

.. contents:: 目录

-------------------

bash快捷键
===========

::

	ctrl + a;   定位光标到命令行首
	ctrl + e;   命令行尾
	!!:1        上一条命令第一个参数。
	!$          上一条命令最后一个参数。

bash编程
========

::

	cd /usr/bin
	# 判断变量是否不包含bak字符
	for i in nova-*; do [[ ! $i =~ "bak" ]] && echo $i ;done

其他
++++

删除文件名包含特殊字符的文件：

::

	mv ./-hl hl.txt

性能调优
========

释放缓存：

::

    echo 3 > /proc/sys/vm/drop_caches

查看内存使用：

::

    free -hl


常用命令
========

常用命令重用用法参考!

nc
++

-	传输目录

	server端：

	::

		tar -cvf - allinone-v2.5-install-script | nc -l 12345

	client端：

	::

		nc -n 192.168.159.146 12345 | tar -xvf -

-	传输文件


	server端：

	::

		nc -l 12345 < file.txt


	client端：

	::

		nc -n 172.31.100.7 1567 > file.txt

然后两端分别使用md5sum命令核对文件传输是否出错.


apt-get
+++++++

只获取包，不安装：

::

	# 如果软件包没有安装
	apt-get -d install git
	# 如果已经安装
	apt-get -d install git --reinstall


awk
+++

::

	# 打印某一行, 自设定分隔符
	awk -F: '{print $1}'
	# 打印除第一行之外的所有行
	awk '{$1="";print $0}'
	# 循环把前N列都赋值为空，从第n+1列开始打印所有的列！
	awk '{ for(i=1; i<=n; i++){ $i="" }; print $0 }' urfile


cut
+++

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


dpkg
++++

查看某软件包是否安装，这两条都可以：

::

	dpkg -s lvm2    
	dpkg-query -l lvm

列出所有安装软件包：

::

	dpkg --get-selections    
	dpkg -l

列出软件包中所有文件位置：

::
	 
	dpkg -L lvm2


get
+++

下载网站的整个目录，以供离线浏览：

.. code:: shell

	wget -c -r -np -k -L -p http://docs.ceph.org.cn

	
scp
+++

::

	# 远程拷贝文件
	scp root@10.11.113.198:/smbshare/win7.raw .
	# 远程拷贝目录
	scp -r root@10.11.113.198:/smbshare/ .

sed
+++

修改文件某一行：

::

	# 终端显示修改后的结果
	sed "s/'metering',/'metering','instances_monitor'/g" txt
	# 直接修改原文件
	sed -i "26s/'metering',/'metering','instances_monitor'/g" dashboard.py


route
+++++

添加路由：

::

	route add -net 224.0.0.0 netmask 240.0.0.0 dev eth0


删除路由：

::

	route del -net 224.0.0.0 netmask 240.0.0.0
	route del -net 224.0.0.0 netmask 240.0.0.0 reject

ps
++

批量杀死进程：

::

	ps -aux|grep name|grep -v grep|cut -c 9-15|xargs kill -9
	ps afx -o pid,cmd | grep nova

df/du
+++++

::

	df -hl
	du -hd1

find/xargs
+++++++++++

::

	find . -type f -name "*.py" | xargs egrep "xxx"
	
	
.. [#] http://yansu.org/2014/01/15/general-shell-resources.html

lsof
++++

::

	lsof -i :5000