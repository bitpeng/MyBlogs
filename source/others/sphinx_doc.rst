
###############################
sphinx模板
###############################



一级标题
================================

二级标题
-------------------------------

*三级标题*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
个人的写作习惯，习惯把三级标题用斜体表示


段落
-------------------------------
REST 是松散的文本结构，使用预定义的模式描述文章的结构。首先学习最基本的结构：段落。
段落是被空行分割的文字片段，左侧必须对齐（没有空格，或者有相同多的空格）。


段落还可以进行缩进;
    REST 是松散的文本结构，使用预定义的模式描述文章的结构。首先学习最基本的结构：段落。
    段落是被空行分割的文字片段，左侧必须对齐（没有空格，或者有相同多的空格）。

段落还可以进行缩进;

    REST 是松散的文本结构，使用预定义的模式描述文章的结构。首先学习最基本的结构：段落。
    段落是被空行分割的文字片段，左侧必须对齐（没有空格，或者有相同多的空格）。

超链接 `超链接 <http://www.baidu.com>`_

单星号: *文本*  强调 (斜体 对中文一般效果不好)

双星号: **文本** 加重 (加黑)

反引号: ``文本`` 代码引用

代码

.. code-block:: python

   a={1: 2, 3: 4}
   pprint.pprint(a)

   {1: 2, 3: 4}

列表和引用块
=============================
只要自然的在段落的开始放置一个星号并正确缩进. 这同样适用于带编号的列表; 也可以使用``#``签署自动编号:

* This is a bulleted list.
* It has two items, the second
  item uses two lines.

1. This is a numbered list.
2. It has two items too.

   #. This is a numbered list.
   #. It has two items too.

#. End.

嵌套的列表是允许的但必须用空行同父列表分离开:

* this is
* a list

  * with a nested list
  * and some subitems

* and here the parent list continues

创建引用段落 (参考)只需要用缩进和其它段落区分即可.

线块 (ref) 是保留换行符的一种方法:

| These lines are
| broken exactly like in
| the source file.


表格
==============================

简单表
-------------------------------

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | ...        | ...      |          |
+------------------------+------------+----------+----------+

网格表
-------------------------------

=====  =====  =======
A      B      A and B
=====  =====  =======
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =======


CSV表格
-------------------------------
.. csv-table:: Frozen Delights!
 :header: "Treat", "Quantity", "Description"
 :widths: 15, 10, 30

 "Albatross", 2.99, "On a stick!"
 "Crunchy Frog", 1.49, "If we took the bones out, it wouldn't be
 crunchy, now would it?"
 "Gannet Ripple", 1.99, "On a stick!"



列表表格
-------------------------------
.. list-table:: Frozen Delights!
  :widths: 15 10 30
  :header-rows: 1

  * - Treat
    - Quantity
    - Description
  * - Albatross
    - 2.99
    - On a stick!
  * - Crunchy Frog
    - 1.49
    - If we took the bones out, it wouldn't be
      crunchy, now would it?
  * - Gannet Ripple
    - 1.99
    - On a stick!


.. _my-reference-label:

Section to cross-reference
--------------------------

This is the text of the section.

It refers to the section itself, see :ref:`my-reference-label`.

..
   #####################################
   # 有上标线, 用以部分
   #####################################

   *****************************
   * 有上标线, 用以章节
   *****************************

   =, 用以小节
   ====================================

   -, 用以子节
   ------------------------------------

   ^, 用以子节的子节
   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   ", 用以段落
   """"""""""""""""""""""""""""""""""""

..
   This whole indented block
   is a comment.

   Still in the comment.



--------

.. [#] “Hello, world”最为程序员所熟知，2002年申请不到helloworld相关域名便\
       退而求其次，申请了 worldhello.net。
.. [#] http://liquidmarkup.org/
.. [#] https://github.com/mojombo/jekyll/wiki/configuration
.. [#] http://docutils-zh-cn.readthedocs.io/zh_CN/latest/index.html#
