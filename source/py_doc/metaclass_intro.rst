.. _metaclass_intro:


Python元类
##########

Python 元类在OpenStack中经常有看到，网络上也有很多很好的阐述，
这里总结下Python元类的用法，作为个人学习笔记。

更多请参考：

.. [#] http://blog.csdn.net/gzlaiyonghao/article/details/3048947
.. [#] http://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python


根据上面的两篇文章，可以知道 ``type`` 两种函数的不同用法：

::

    type(obj)  # 返回 obj 的类型；
    # 动态的创建类！
    type(name, bases, _dict)

Python ``six.add_metaclass`` 可以用来实现给类增加 __metaclass__ 属性的效果，这是一个函数装饰器，
源码看起来也非常的简单。来看看这个例子：

::

    #!/usr/bin/env python

    def metaclass(metaclass):
        """Class decorator for creating a class with a metaclass."""
        def wrapper(cls):
            orig_vars = cls.__dict__.copy()
            orig_vars.pop('__dict__', None)
            orig_vars.pop('__weakref__', None)
            slots = orig_vars.get('__slots__')
            if slots is not None:
                if isinstance(slots, str):
                    slots = [slots]
                for slots_var in slots:
                    orig_vars.pop(slots_var)
            return metaclass(cls.__name__, cls.__bases__, orig_vars)
        return wrapper

    class UpperAttrMetaclass(type):

        def __new__(cls, clsname, bases, dct):

            uppercase_attr = {}
            for name, val in dct.items():
                if not name.startswith('__'):
                    uppercase_attr[name.upper()] = val
                else:
                    uppercase_attr[name] = val

            return super(UpperAttrMetaclass, cls).__new__(cls, clsname, bases, uppercase_attr)
            #return type(clsname, bases, uppercase_attr)

    #b = UpperAttrMetaclass()
    class B1(object):
        __metaclass__ = UpperAttrMetaclass
        bar = 'bar'
        foo = 'foo'
        def __init__(self):
            return super(B1, self).__init__()

    b1 = B1(); print dir(b1)
    print b1.BAR
    #print b1.bar

    #@six.add_metaclass(UpperAttrMetaclass)
    @metaclass(UpperAttrMetaclass)
    class B2(object):
        #__metaclass__ = UpperAttrMetaclass
        bar2 = 'bar2'
        foo2 = 'foo2'
        # __slots__ = ("bar2", "fo2")
        def __init__(self):
            return super(B2, self).__init__()

    #B2=metaclass(UpperAttrMetaclass)(B2)
    b2 = B2(); print dir(b2)
    print "B2.__dict__, ", B2.__dict__
    print "b2.__dict__, ", b2.__dict__
    b2.a = "a"
    print "b2.__dict__, ", b2.__dict__
    b2.dic = "dic"
    #print b2.__slots__
    #print b1.BAR
    print type(B2)

在这里的测试中，我使用了两种方式来测试元类：

- 第一种是给 :class:`B1` 类增加 `__metaclass__` 属性；
- 第二种是给 :class:`B2` 类使用 :func:`metaclass` 装饰器(源码拷贝于 :func:`six.add_metaclass` )

我们来看看第二种方式，通过这种方式，可以了解元类的本质。

在 :func:`metaclass` 中，以 :class:`B2` 为例，讲解该函数的执行过程：

- 首先获取 :class:`B2` 字典属性;
- 假如 :class:`B2` 存在 __slots__ 属性，则从字典属性中移除相应的items；
- 使用元类 :class:`UpperAttrMetaclass` 生成类 :class:`B2`

在 :class:`UpperAttrMetaclass` 的 __new__ 魔法方法中，
针对类的每一个非特殊属性，将属性名称转换成大写方式。因此 B2.foo2
和 B2.bar2 都被转换成大写的形式，然后生成类 B2。

综上，我们可以很清晰的看到，元类是怎样拦截类的创建的！
