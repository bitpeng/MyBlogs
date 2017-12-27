.. _linux_time_zone:


########################
Linux时间与时区问题
########################

.. contents:: 目录

--------------------------

本文探讨内容基于ubuntu-14.04-LTS系统。


问题
=====

在ubuntu系统上搭建了mantis bug tracker，结果提交问题时，时间一直显示有问题，
经过排查，发现是ubuntu系统时区设置问题。


.. code-block:: console

    root@14-04-server:/home/wangxing# date 
    Tue Dec 26 17:00:48 EST 2017
    root@14-04-server:/home/wangxing# 
    root@14-04-server:/home/wangxing# 
    root@14-04-server:/home/wangxing# date -R
    Tue, 26 Dec 2017 17:03:58 -0500


.. figure:: /_static/images/mantis_zone_set.png
   :scale: 100
   :align: center

   mantisbt时区设置显示时上海时区


``date`` 命令显示系统设置的时区为EST(美国东部时区)，而mantisbt设置的为上海时区，
因此mantis时间问题显示上，会将系统(EST)时间转换成上海时间，因此导致mantis时间显示错误。


解决方案
========

解决这个问题，只需要将系统时区正确设置正确即可。

::

    dpkg-reconfigure tzdata
    
.. figure:: /_static/images/config_tzdata.png
   :scale: 100
   :align: center

   安装提示将时区设置为上海时区
   
然后使用时间同步服务更新系统时间。

::

    ntpdate cn.pool.ntp.org

需要注意几点：

- 参考网络上的相关教程，说时间同步后，还需要执行以下命令：
  
  ::
     
    sudo cp /usr/share/zoneinfo/Asia/Chongqing /etc/localtime
    hwclock -w

  但是我在我的ubuntu-14.04-LTS系统上，无需执行上面两条命令，系统重启后，
  时间配置一样正确。
  
- ntpdate命令会跳跃性的更新系统时间，这可能会导致严重的问题。
  因此推荐使用ntpd/adjtimex，平滑更新系统时间。具体请自行参考相关内容。
  
  
相关概念
========  

.. attribute:: 硬件时钟

    又称为CMOS时钟、BIOS时钟、RTC、硬时钟等。由电池供电，用于跟踪系统关闭后的运行时间，
    系统运行时他不使用。
    
.. attribute:: 系统时钟

    也称为软时钟，系统关闭时不存在，系统启动后从RTC初始化。

**硬件时间存放在 RTC(Real Time Clock) 硬件中。
Linux 系统启动时，会读取 RTC 时间，并该时间来初始化系统时间；
正常运行时，系统时间在每次 tick 中断中加以更新和维护；当系统关闭时，
Linux 用系统时间来更新硬件时间。**

.. attribute:: UTC

    UTC 就是 Coordinated Universal Time，是全世界通用的时间标准。
    它是格林威治时间 (GMT) 的后继者，在计算机领域，GMT 术语不再广泛使用，
    因为它的精度不够高。UTC 是 1963 年标准化的，采用了高精度的原子钟。
    因此在科学领域，包括计算机科学，都采用 UTC 而不再使用 GMT 这个术语。
    我们可以认为 UTC 就是时区 0 的标准时间。
    
.. attribute:: LCT

    LCT(Local Civil Time) 即当地时间，比如北京时间。
  
相关命令
=========

::

    # 查看系统时区信息
    timedatectl

    # 显示硬件时钟与日期
    hwclock –r         
    # 将系统时钟调整为与目前的硬件时钟一致
    hwclock –s         
    # 将硬件时钟调整为与目前的系统时钟一致
    hwclock –w         
    
    # 该配置文件有一个关键配置项，UTC，指示系统硬件时间是UTC时间还是本地时间
    vim /etc/default/rcS
    
    # 显示日期、时间、时区等。
    date
    date -R
    
    # 配置系统时区
    dpkg-reconfigure tzdata

---------------------

参考
=====

.. [#] 对硬件时钟，系统时钟，UTC，LCT以及他们的转化关系有比较详细的介绍。 网址：https://www.ibm.com/developerworks/cn/linux/1308_liuming_linuxtime4/index.html
.. [#] 介绍了ubuntu系统时钟、硬件时钟相关概念和命令。 网址： http://manpages.ubuntu.com/manpages/trusty/en/man8/clock.8.html
.. [#] 对Linux系统时间同步问题有比较详细的介绍。网址：http://www.tldp.org/HOWTO/Clock-2.html
.. [#] https://www.cnblogs.com/sky-heaven/p/5220873.html
.. [#] http://blog.csdn.net/w786572258/article/details/51248053


