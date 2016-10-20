Python描述器
============

tags： Python

--------------

[TOC]

--------------

要点
----

-  描述器只对新式类起作用；
-  如果访问ojb.attr，其中attr既是obj的实例属性，也是obj的一个描述器时，到底访问的哪个attr取决于attr描述器的类型。优先级是：资源描述器
   -> 实例字典 -> 非资源描述器。请看示例一：
-  把描述符放在类的层次上：为了让描述符能够正常工作，它们必须定义在类的层次上。如果你不这么做，那么Python无法自动为你调用\_\_get\ **和**\ set\_\_方法。
-  确保实例的数据只属于实例本身。

.. code:: python

    # 示例一
    # 非资源描述器
    class cached_property(object):
        def __init__(self, func, name=None, doc=None):
            self.__name__ = name or func.__name__
            self.__module__ = func.__module__
            self.__doc__ = doc or func.__doc__
            self.func = func

        def __get__(self, obj, type=None):
            if obj is None:
                return self
            value = obj.__dict__.get(self.__name__, _missing)
            if value is _missing:
                value = self.func(obj)
                obj.__dict__[self.__name__] = value
            return value

    # 资源描述器
    class cached_property_2(object):
        def __init__(self, func, name=None, doc=None):
            self.__name__ = name or func.__name__
            self.__module__ = func.__module__
            self.__doc__ = doc or func.__doc__
            self.func = func

        def __get__(self, obj, type=None):
            if obj is None:
                return self
            value = obj.__dict__.get(self.__name__, _missing)
            if value is _missing:
                value = self.func(obj)
                obj.__dict__[self.__name__] = value
            return value

        def __set__(self, obj, value):
            pass

    class Foo(object):
        def __init__(self):
            self.f1 = "name f1"
            self.f2 = "instance f2"
            self.tt = cached_property(test1)
            pass

        @cached_property
        def f1(self):
            print 'first f1,,', 
            result = 'this is result'
            return result
        # f1 = cached_property(f1)

        @cached_property_2
        def f2(self):
            print 'first f2,,', 
            return "description f2"

    def test1():
        f = Foo()

        print f.f1   # first calculate this is result
        print f.f1   # this is result

        print f.f2
        print f.f2

请参考：

http://pyzh.readthedocs.io/en/latest/Descriptor-HOW-TO-Guide.html

http://blog.csdn.net/huithe/article/details/7484606

http://hbprotoss.github.io/posts/python-descriptor.html

http://www.jianshu.com/p/250f0d305c35

http://xiaorui.cc/2015/08/30/python%E9%AD%94%E6%B3%95%E5%87%BD%E6%95%B0%E4%B8%AD%E7%9A%84%E6%8F%8F%E8%BF%B0%E5%99%A8descriptor/

https://segmentfault.com/a/1190000004238416

http://strawhatfy.github.io/2015/04/21/python-attribute-lookup/

http://xiaorui.cc/2015/08/30/python%E9%AD%94%E6%B3%95%E5%87%BD%E6%95%B0%E4%B8%AD%E7%9A%84%E6%8F%8F%E8%BF%B0%E5%99%A8descriptor/

-  http://python.jobbole.com/81899/
-  http://python.jobbole.com/81899/

http://www.jianshu.com/p/250f0d305c35

http://pyzh.readthedocs.io/en/latest/Descriptor-HOW-TO-Guide.html

https://segmentfault.com/a/1190000004238416

http://blog.jobbole.com/61171/
