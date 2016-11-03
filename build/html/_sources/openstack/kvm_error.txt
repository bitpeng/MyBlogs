.. _kvm_error:


########################
KVM错误问题
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::

    在vmware里面用kvm启动虚拟机，发现无法启动，实际上问题很简单，但是由于多次犯了该错误，因此记录下来。


.. contents:: 目录

--------------------------


问题
========


allinone环境下，安装了qemu-kvm命令后，启动虚拟机，提示错误。

.. figure:: /_static/images/kvm_error.png
   :scale: 100
   :align: center

   KVM启动虚拟机错误


解决方案
========

实际上，这个问题已经多次遇到了，但是每次还是会犯错。非常简单，就是CPU没有开启虚拟化。
并且，google后，前几页就是该链接就是该问题。

.. figure:: /_static/images/kvm_google.png
   :scale: 100
   :align: center

   Google 解决之

.. important::

    - 犯过的错误一定要避免二次错误；
    - 多google，可以解决大部分问题；

---------------------

参考
=====

.. [#] http://f.dataguru.cn/thread-127360-1-1.html
.. [#] http://askubuntu.com/questions/140360/kvm-kernel-module-error

