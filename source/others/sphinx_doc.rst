
###############################
sphinx模板
###############################






一级标题
================================

二级标题
-------------------------------

三级标题
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
   
+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | ...        | ...      |          |
+------------------------+------------+----------+----------+

网格表

=====  =====  =======
A      B      A and B
=====  =====  =======
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =======


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
