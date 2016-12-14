###############################
善用Linux man page
###############################


.. contents:: 目录

------------------

章节介绍
================================

Linux man page一般包含以下内容:

* 1   可执行程序和shell命令
* 2   (内核提供的)系统调用
* 3   库函数
* 4   特殊文件(一般位于/dev)
* 5   文件格式规范
* 6   游戏
* 7   杂项(包括包和规范)
* 8   系统管理命令(只对root可用)
* 9   内核例程


查询指定章节
================================

例如printf，既是一个shell命令，也是一个C库函数，我们可以通过指定章节查询相应的手册页。

**查询printf命令**
::

    man 1 printf


**查询printf函数**
::

    man 3 printf


列出所有章节
============

可以使用下面的命令：

::

    man -aw printf
    man -a printf



搜索在线手册
============

**指定关键字**

::

    man -k printf

**正则搜索**

::

    man -k "^s.*printf"
    apropos "^s.*printf"


指定语言
=========
甚至我们可以指定man page的语言，可是由于中文man page许久没有更新，有些过时。因此建议大家直接查看英文在线手册！



高亮显示
========
在我使用的Ubuntu系统中，man page命令默认显示黑白色。如图1所示:

.. figure:: /_static/images/img-black_color.png
   :scale: 100
   :align: center

   图1：默认黑白色显示

..
   centered:: 图1：默认黑白色显示

我们可以通过手动设置，让man输出高亮显示, 把下面代码追加到/etc/bash.bashrc即可。

.. literalinclude:: /_static/src/src-highlight_man.sh
   :language: sh
   :linenos:

更改后高亮效果如下所示，很美观吧。

..
   figure:: img-highlight_color.png
   :scale: 100

.. figure:: /_static/images/img-highlight_color.png
   :scale: 100
   :align: center

   图2：高亮输出







--------


参考
================================

.. [#] https://blog.gtwang.org/linux/linux-man-page-command-examples/
