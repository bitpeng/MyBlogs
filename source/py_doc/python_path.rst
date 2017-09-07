.. _py_path:


########################
Python文件与目录操作
########################



.. contents:: 目录

--------------------------



本文对Python文件和目录操作的问题做个总结。



获取文件绝对目录
==================

获取文件的绝对目录，请看下面的测试代码：

.. code-block:: python

    # path_test.py
    import os

    print "__file__:", __file__
    #print "type(__file__):", type(__file__)

    print "__name__:", __name__

    print "os.path.dirname(__file__):", os.path.dirname(__file__)
    print "os.path.abspath(__file__):", os.path.abspath(__file__)
    print "os.path.dirname(os.path.abspath(__file__)):", os.path.dirname(os.path.abspath(__file__))

    print "getcwd():", os.getcwd()


.. code-block:: python

    # path_test-2.py
    import path_test


这两个文件，都放在/smbshare/目录下：

::

    root@ubuntu:/smbshare# ls path_test*
    path_test-2.py  path_test.py  path_test.pyc


然后在不同的目录，依次执行两个程序。首先在源文件所在目录/smbshare下执行：

.. code-block:: console

    root@ubuntu:/smbshare# python path_test.py
    __file__: path_test.py
    __name__: __main__
    os.path.dirname(__file__): 
    os.path.abspath(__file__): /smbshare/path_test.py
    os.path.dirname(os.path.abspath(__file__)): /smbshare
    getcwd(): /smbshare
    root@ubuntu:/smbshare# 
    root@ubuntu:/smbshare# python path_test-2.py 
    __file__: /smbshare/path_test.pyc
    __name__: path_test
    os.path.dirname(__file__): /smbshare
    os.path.abspath(__file__): /smbshare/path_test.pyc
    os.path.dirname(os.path.abspath(__file__)): /smbshare
    getcwd(): /smbshare


然后在另外一个目录下执行：

.. code-block:: console

    root@ubuntu:/usr/local/lib# python /smbshare/path_test.py
    __file__: /smbshare/path_test.py
    __name__: __main__
    os.path.dirname(__file__): /smbshare
    os.path.abspath(__file__): /smbshare/path_test.py
    os.path.dirname(os.path.abspath(__file__)): /smbshare
    getcwd(): /usr/local/lib
    root@ubuntu:/usr/local/lib# 
    root@ubuntu:/usr/local/lib# python /smbshare/path_test-2.py 
    __file__: /smbshare/path_test.pyc
    __name__: path_test
    os.path.dirname(__file__): /smbshare
    os.path.abspath(__file__): /smbshare/path_test.pyc
    os.path.dirname(os.path.abspath(__file__)): /smbshare
    getcwd(): /usr/local/lib


**在不同的目录下，以及通过直接执行和导入执行，__file__变量代表的值都是不一样的。因此，在程序中，
绝对不可以用__file__来获取文件的路径。**

通过程序运行结果，可以看到：假如想获取文件的绝对全路径，只可以用 ``os.path.abspath(__file__)`` ，
如果想获取文件所在的完整目录：只可以用 ``os.path.dirname(os.path.abspath(__file__))`` 。


另外值得一提的是，自己原来也使用过这样的方式，来获取与当前文件在同一个目录的文件绝对路径：

::

    abs_path = os.path.abspath(__file__)
    name = ["glusterrest.ini"]
    return '/'.join(abs_path.split("/")[:-1] + name)


文件和目录操作
================

目录下所有文件
++++++++++++++

::

    >>> os.listdir('.')
    ['.idea', 'db.sqlite3', 'manage.py', 'demo', 'static', 'templates', 'dj_websocket']


获取文件属性
+++++++++++++

::

    >>> os.stat('manage.py')
    posix.stat_result(st_mode=33188, st_ino=7602258, st_dev=64512L, 
    st_nlink=1, st_uid=0, st_gid=0, st_size=810, st_atime=1504676329, 
    st_mtime=1504589646, st_ctime=1504589646)


根据文件属性获取文件用户、组信息
++++++++++++++++++++++++++++++++

::

    >>> import pwd
    >>> pw = pwd.getpwuid(0)
    >>> 
    >>> pw
    pwd.struct_passwd(pw_name='root', pw_passwd='x', pw_uid=0, 
    pw_gid=0, pw_gecos='root', pw_dir='/root', pw_shell='/bin/bash')
