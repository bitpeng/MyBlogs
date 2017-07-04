.. _mysql_note:


########################
mysql相关
########################


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

    # 查找前十条记录
    select * from <T> limit 0, 10;
    # 查找最后五条记录
    select * from <T> order by id desc limit 5;


shell中执行MySQL命令
=====================

有时会遇到一些场景，需要在shell脚本中执行MySQL命令。比如，我曾经遇到，
OpenStack登录认证响应过慢，经确定，是keystone认证生成的token都保存在数据库中，影响MySQL读性能，
进而影响keystone认证。因此，需要确定，keystone数据库中，各个表的记录数和占用的空间！

假如在MySQL命令行下，一条一条命令的执行，查看每个表占用的空间，那真的太麻烦了。后来，
经过一番学习，简单写了个shell脚本。

::

    #!/usr/bin/env bash

    #set -ex

    mysql <<EOF  > keystone_tables
        use keystone;
        show tables;
    EOF

    #echo 'use information_schema;' >> count_length.sql;
    echo 'use information_schema;' > count_length.sql;

    while read line
    do
        # echo $line
        select="SELECT TABLE_NAME,DATA_LENGTH+INDEX_LENGTH,TABLE_ROWS FROM TABLES WHERE TABLE_SCHEMA='keystone' AND TABLE_NAME='$line';"
        echo $select >> count_length.sql
    done < keystone_tables

    mysql < count_length.sql

在这个脚本中，先把keystone的每一个表，保存在文件keystone_tables中，然后对于每一个表，
查找它的表名，占用空间，表记录数等(把MySQL查询语句保存在count_length.sql文件中)。
以下是脚本的执行结果：

.. code-block:: console

    root@allinone-v2:/smbshare# ./shell_mysql.sh 
    TABLE_NAME  DATA_LENGTH+INDEX_LENGTH    TABLE_ROWS
    assignment  49152   9
    TABLE_NAME  DATA_LENGTH+INDEX_LENGTH    TABLE_ROWS
    credential  16384   0
    TABLE_NAME  DATA_LENGTH+INDEX_LENGTH    TABLE_ROWS
    domain  32768   1
    TABLE_NAME  DATA_LENGTH+INDEX_LENGTH    TABLE_ROWS
    endpoint    49152   27
    TABLE_NAME  DATA_LENGTH+INDEX_LENGTH    TABLE_ROWS
    group   32768   0
    TABLE_NAME  DATA_LENGTH+INDEX_LENGTH    TABLE_ROWS
    id_mapping  32768   0

实际上，对于输出结果，我们还可以利用awk工具，进行格式化输出。这一步的工作，待以后完善！



---------------------

参考
=====

.. [#] http://www.jb51.net/article/85218.htm
