.. _py_time_date:


########################
Python时间和日期操作
########################


.. contents:: 目录

--------------------------

Python时间和日期操作，总是容易搞混淆，现在对相关库的用法坐下总结！


相关对象
============

::

    >>> import time
    >>> 
    >>> 
    >>> time.localtime()
    time.struct_time(tm_year=2017, tm_mon=6, tm_mday=13, tm_hour=23, tm_min=20, tm_sec=48, tm_wday=1, tm_yday=164, tm_isdst=1)
    >>> 
    >>> 
    >>> time.strptime("2017-5-3",'%Y-%m-%d')
    time.struct_time(tm_year=2017, tm_mon=5, tm_mday=3, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=2, tm_yday=123, tm_isdst=-1)
    >>> 
    >>> time.strptime("2017-5-3 13:20:5",'%Y-%m-%d %H:%M:%S')
    time.struct_time(tm_year=2017, tm_mon=5, tm_mday=3, tm_hour=13, tm_min=20, tm_sec=5, tm_wday=2, tm_yday=123, tm_isdst=-1)

::

    >>> import datetime
    >>> now = datetime.datetime.now()
    >>> now
    datetime.datetime(2017, 6, 13, 23, 27, 41, 421889)
    >>> 
    >>> t = datetime.datetime(2017, 5, 13, 21, 12, 43)
    >>> 
    >>> t
    datetime.datetime(2017, 5, 13, 21, 12, 43)
    >>> 
    >>> t.strftime("%Y-%m-%d %H:%M:%S")
    '2017-05-13 21:12:43'




转化关系
=========


tuple <--> string
++++++++++++++++++

::

    >>> ttu = time.strptime("2017-5-3 13:20:5",'%Y-%m-%d %H:%M:%S')
    >>>
    >>> ttu
    time.struct_time(tm_year=2017, tm_mon=5, tm_mday=3, tm_hour=13, tm_min=20, tm_sec=5, tm_wday=2, tm_yday=123, tm_isdst=-1)
    >>> time.strftime("%Y-%m-%d %H:%M", ttu)
    '2017-05-03 13:20'
    >>>
    >>> time.strptime("2017-5-3 13:20:5",'%Y-%m-%d %H:%M:%S')
    time.struct_time(tm_year=2017, tm_mon=5, tm_mday=3, tm_hour=13, tm_min=20, tm_sec=5, tm_wday=2, tm_yday=123, tm_isdst=-1)


datetime <--> string
+++++++++++++++++++++

::

    >>> t = datetime.datetime(2017, 5, 13, 21, 12, 43)
    >>> 
    >>> t
    datetime.datetime(2017, 5, 13, 21, 12, 43)
    >>> 
    >>> t.strftime("%Y-%m-%d %H:%M:%S")
    '2017-05-13 21:12:43'
    >>> 
    >>> datetime.datetime.strptime("2014-12-31 18:20:10", "%Y-%m-%d %H:%M:%S")
    datetime.datetime(2014, 12, 31, 18, 20, 10)


datetime <--> timetuple
++++++++++++++++++++++++

::

    >>> now = datetime.datetime.now()
    >>> now
    datetime.datetime(2017, 6, 13, 23, 53, 10, 530091)
    >>> 
    >>> now.timetuple()
    time.struct_time(tm_year=2017, tm_mon=6, tm_mday=13, tm_hour=23, tm_min=53, tm_sec=10, tm_wday=1, tm_yday=164, tm_isdst=-1)
    >>> 
    >>> ntu = now.timetuple()
    >>> 
    >>> ntu
    time.struct_time(tm_year=2017, tm_mon=6, tm_mday=13, tm_hour=23, tm_min=53, tm_sec=10, tm_wday=1, tm_yday=164, tm_isdst=-1)


而timetuple转化为datetime，可以先转化为timestamp。

::

    >>> ntu
    time.struct_time(tm_year=2017, tm_mon=6, tm_mday=13, tm_hour=23, tm_min=53, tm_sec=10, tm_wday=1, tm_yday=164, tm_isdst=-1)
    >>> 
    >>> ts = time.mktime(ntu)
    >>> 
    >>> ts
    1497423190.0
    >>> 
    >>> datetime.datetime.fromtimestamp(ts)
    datetime.datetime(2017, 6, 13, 23, 53, 10)


时间戳转换成成string
++++++++++++++++++++++

两种方法：

::

    >>> ts
    1497423190.0
    >>> 
    >>> time.ctime(ts)
    'Tue Jun 13 23:53:10 2017'
    >>> 
    >>> import datetime
    >>> datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    '2017-06-13 23:53:10'


其他转化
+++++++++

::

    >>> ts
    1497423190.0
    >>> ntu
    time.struct_time(tm_year=2017, tm_mon=6, tm_mday=13, tm_hour=23, tm_min=53, tm_sec=10, tm_wday=1, tm_yday=164, tm_isdst=-1)
    >>> 
    >>> time.ctime(ts)
    'Tue Jun 13 23:53:10 2017'
    >>> time.asctime(ntu)
    'Tue Jun 13 23:53:10 2017'

盗用网上的一张图。理解了以上这些，基本可以满足日常编码需要，以后有需要，再继续补充吧！

.. figure:: /_static/images/time_convert.png
   :scale: 100
   :align: center

   转化关系图


参考
======

.. [#] http://www.wklken.me/posts/2015/03/03/python-base-datetime.html
