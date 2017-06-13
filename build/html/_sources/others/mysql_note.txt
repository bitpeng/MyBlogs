.. _mysql_note:


########################
mysql相关
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^




.. contents:: 目录

--------------------------


mysql权限
==========

今天尝试使用Navicat数据库可视化工具，使用Navicat for mysql工具连接ubuntu时，连接不上，经查，
这里涉及到MySQL权限问题。主要是下面几条：

::

	# 赋予MySQL myuser用户从任何主机访问数据库的权限。
	GRANT ALL PRIVILEGES ON *.* TO 'myuser'@'%'IDENTIFIED BY 'mypassword' WI 
	TH GRANT OPTION;
	FLUSH PRIVILEGES;


	# 赋予MySQL root用户从192.168.159.1访问访问数据库的权限。
	GRANT ALL PRIVILEGES ON *.* TO 'root'@'192.168.159.1'IDENTIFIED BY
	'httc123' WITH GRANT OPTION;
	FLUSH PRIVILEGES;


	# 赋予任何主机访问访问数据库的权限。
	GRANT ALL PRIVILEGES ON *.* TO 'root'@'%'WITH GRANT OPTION;
	FLUSH PRIVILEGES;

经过合适的权限设置，然后就可以使用Navicat连接MySQL数据库了。效果如下！

.. figure:: /_static/images/Navicat_for_mysql.png
   :scale: 100
   :align: center


MySQL相关命令
==============

::

    show databases;
    show tables;
    use <db>;
    desc <table>;

    select * from <T> limit 0, 10;


---------------------

参考
=====

.. [#] http://www.jb51.net/article/85218.htm
