.. rst_usage:

rst 用法自我总结
#################


.. contents:: 目录

--------------------------



锚点链接
========

::


    .. _link_text:

    :ref:`点击链接<link_text>`

.. _link_text:

:ref:`点击链接<link_text>`


代码相关
========

普通代码定义：

::

    ::

        import sys
        from mod import main
        if __name__ == "__main__":
            sys.exit(main())

效果：

::

    import sys
    from mod import main
    if __name__ == "__main__":
        sys.exit(main())

高亮代码定义，带行号：

::

    .. code-block:: python|console
        :linenos:
    
        import sys
        from mod import main
        if __name__ == "__main__":
            sys.exit(main())

.. code-block:: python
    :linenos:

    import sys
    from mod import main
    if __name__ == "__main__":
        sys.exit(main())

高亮代码定义2：

.. code:: python

    import sys
    from mod import main
    if __name__ == "__main__":
        sys.exit(main())

引用代码文件：

::

    .. literalinclude:: /_static/src/test_cfg.py
        :language: python
        :linenos:



引用图片
========

::

    .. figure:: /_static/images/kvm_error.png
       :scale: 100
       :align: center

       KVM启动虚拟机错误

注释
=====

::

    ..
        这是注释
        这也是注释

..
    这是注释
    这也是注释

其他
====

* :meth:`~Handler.setFormatter` selects a Formatter object for this handler to
  use.

.. method:: logging.Formatter.__init__(fmt=None, datefmt=None)

If there is no message format string, the default is to use the 
raw message.  If there is no date format string, the default date format is::

    %Y-%m-%d %H:%M:%S


.. |date| date::

Today's date is |date|.
