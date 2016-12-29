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

正则匹配
+++++++++

::

    cd /usr/bin
    # 判断变量是否不包含bak字符
    for i in nova-*; do [[ ! $i =~ "bak" ]] && echo $i ;done

特殊字符处理
+++++++++++++

删除文件名包含特殊字符的文件：

::

    mv ./-hl hl.txt

重定向
+++++++

shell输入输出重定向：

::

    ls > log
    ls 1> log
    ls 2> log
    ls &> log
    ls 1> log 2> /dev/null

字符串截取
++++++++++


::

    url='http://10.10.10.10:35357/v2.0'
    # 从最左边开始删除
    echo ${SERVICE_ENDPOINT#*//}
    # 
    echo ${SERVICE_ENDPOINT##*/}

.. [#] http://www.linuxidc.com/Linux/2015-03/115198.htm


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

常用命令常用用法参考!

nc
++

-   传输目录

    server端：

    ::

        tar -cvf - allinone-v2.5-install-script | nc -l 12345

    client端：

    ::

        nc -n 192.168.159.146 12345 | tar -xvf -

-   传输文件


    server端：

    ::

        nc -l 12345 < file.txt


    client端：

    ::

        nc -n 172.31.100.7 12345 > file.txt

然后两端分别使用md5sum命令核对文件传输是否出错.


apt-get
+++++++

只获取包，不安装：

::

    # 如果软件包没有安装
    apt-get -d install git
    # 如果已经安装
    apt-get -d install git --reinstall

更新安装包索引：

::

    apt-get update

升级已经安装的所有软件包：

::

    apt-get upgrade

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


wget
++++

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

::

    # 批量杀死进程：
    ps -aux|grep name|grep -v grep|cut -c 9-15|xargs kill -9
    # 显示进程的父子关系
    ps afx -o pid,cmd | grep nova
    # 查看某bash的进程树
    ps f

df/du
+++++

::

    df -hl
    du -hd1
    # 列出某个文件或目录占用的空间
    du -sh dir

find/xargs
+++++++++++

::

    find . -type f -name "*.py" | xargs egrep "xxx"


.. [#] http://yansu.org/2014/01/15/general-shell-resources.html

lsof
++++

::

    lsof -i :5000


ln
++

::

    # 建立硬链接
    ln srcfile dstfile
    # 建立软连接
    ln -s srcfile dstfile

    # 显示软硬连接文件详情和区别、inode节点数！
    ll tf-* -i
    # 663182 -rw-r--r-- 2 root root  0 Dec  1 06:59 tf-hl
    # 663237 lrwxrwxrwx 1 root root 13 Dec  1 07:01 tf-sl -> tmp/test-file
    ll -i tmp/test-file
    # 663182 -rw-r--r-- 2 root root 0 Dec  1 06:59 tmp/test-file



ln命令需要特别注意如下几点：

.. - ln 命令用法有点不符合常识，一般都是源文件、目的文件顺序，该命令恰好相反。

- 建立硬链接时拷贝inode节点。硬链接文件是普通文件(文件类型位为 ``-`` )，永远不要建立目录的硬链接。
- 软连接可以连接文件、目录，inode节点数没有增加，文件类型位为 ``l`` 。


grep
++++

::

    # -P: 使用 pcre 模式搜索
    # -v: 表示搜索不匹配的！
    git status | grep -Pv '\.pyc$'

    # 搜索固定字符串, 否则 + 会被当成元字符
    fgrep '+++===+++' /var/log/apache2/error.log

    # 递归搜索
    # -r: 递归搜索，不跟从符号链接！
    fgrep -rn '+++===+++' .


系统和内核信息
++++++++++++++

可以使用下面的命令

::

    cat /etc/issue
    lsb_release -a
    uname -a

