.. _html_note:


########################
HTML 与前端
########################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. tip::

    html 开发与前端相关基础知识笔记


.. contents:: 目录

--------------------


button标签
==========

<button> 标签定义一个按钮。

<button> 控件 与 <input type="button"> 相比，提供了更为强大的功能
和更丰富的内容。<button> 与 </button> 标签之间的所有内容都是按钮的
内容，其中包括任何可接受的正文内容，比如文本或多媒体内容。例如，我
们可以在按钮中包括一个图像和相关的文本，用它们在按钮中创建一个吸引人的标记图像。

.. note::

    请始终为按钮规定 type 属性。Internet Explorer 的默认类型
    是 "button"，而其他浏览器中（包括 W3C 规范）的默认值是 "submit"。

    .. figure:: /_static/images/button_type.png
       :scale: 100
       :align: center

       button type 属性取值

.. important::

    关于button，自己在阅读openstack代码时一直有一点困惑的地方，就是在点击
    按钮时，对应的处理程序在哪里。现在把这个问题记录下来，以作总结。


- button点击按钮后，假如在页面js中有相关的处理，则会调用相应的事件处理程序.(在前端执行，与服务端无关)

  .. literalinclude:: /_static/src/button_test.html
     :language: html
     :linenos:


  如上代码，点击按钮后，都会在调用客户端的click事件处理程序。

- 假如button包含在form中，那么点击表单，则会向服务端提交表单。然后服务端会调用相应的表单处理程序。

  对于django框架来说，通过from提交时 的action，依据URL匹配来决定调用的view(表单处理程序)。

  比如在《django book 2.0》给出的示例中，表单的action="/search/"，因此点击按钮，会根据url.py，决定调用
  view.py的search函数。

  .. figure:: /_static/images/form_temp.png
     :scale: 100
     :align: center

     表单的action属性

  .. figure:: /_static/images/button_action.png
     :scale: 100
     :align: center

     提交表单时服务端会调用view.search 处理程序。

  至于表单提交的GET和POST方法，会在另外一篇文章专门分析。




input type="submit" 和"button"区别分析
======================================

在一个页面上画一个按钮，有四种办法：

- <input type="button" /> 这就是一个按钮。如果你不写javascript 的话，按下去什么也不会发生。
- <input type="submit" /> 这样的按钮用户点击之后会自动提交 form，除非你写了javascript 阻止它。
- <button> 这个按钮放在 form 中也会点击自动提交，比前两个的优点是按钮
  的内容不光可以有文字，还可以有图片等多媒体内容。（当然，前两个用图片背
  景也可以做到）。它的缺点是不同的浏览器得到的 value 值不同；可能还有其他的浏览器兼容问题
- 其他标签，例如 a, img, span, div，然后用图片把它伪装成一个按钮。

可以参考\ `[原]<button>和<input type="button"> 的区别 <http://www.cnblogs.com/purediy/archive/2012/06/10/2544184.html>`__\


---------------------

参考
=====

.. [#] http://www.w3school.com.cn/tags/att_button_type.asp
.. [#] https://www.zhihu.com/question/20839977
.. [#] http://djangobook.py3k.cn/2.0/chapter07/

