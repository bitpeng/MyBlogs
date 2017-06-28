.. _setup:


########################
python打包和发布
########################



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

.. [#] http://yansu.org/2013/06/07/learn-python-setuptools-in-detail.html
.. [#] http://wsfdl.com/python/2015/09/06/Python%E5%BA%94%E7%94%A8%E7%9A%84%E6%89%93%E5%8C%85%E5%92%8C%E5%8F%91%E5%B8%83%E4%B8%8A.html
