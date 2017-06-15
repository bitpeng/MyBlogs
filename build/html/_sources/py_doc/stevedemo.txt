.. _stevedemo:


########################
stevedore库学习
########################


.. contents:: 目录

--------------------------


stevedore库是OpenStack社区在开发ceilometer项目时设计的一个插件框架。
为了更好地理解ceilometer项目代码，现在来学习下该框架。

需要说明的是，在stevedore库源码里面，有一个example目录，包含了利用stevedore定义插件、加载插件的完整例子。
由于stevedore使用setuptools的entry points来定义并加载插件，为了同时理解setuptools库，
下面基于该例子简单修改代码，来定义和加载插件。

代码结构
=========

整个例子的代码结构如下：

::

    root@allinone-v2:/smbshare# tree stevedemo/
    stevedemo/
    ├── setup.py
    └── stevedemo
        ├── base.py
        ├── base.pyc
        ├── fields.py
        ├── fields.pyc
        ├── __init__.py
        ├── __init__.pyc
        ├── load_as_driver.py
        ├── load_as_extension.py
        ├── simple.py
        └── simple.pyc

使用stevedore给应用程序添加插件支持，非常简单。可以分为定义插件，声明插件，加载插件，执行接口四个步骤。

定义插件
========

base.py文件对应着定义插件的抽象类：

::

    import abc 
    import six 

    @six.add_metaclass(abc.ABCMeta)
    class FormatterBase(object):
        """Base class for example plugin used in the tutoral.
        """

        def __init__(self, max_width=60):
            self.max_width = max_width

        @abc.abstractmethod
        def format(self, data):
            """Format the data and return unicode text.

            :param data: A dictionary with string keys and simple types as
                         values.
            :type data: dict(str:?)
            :returns: Iterable producing the formatted text.
            """

然后定义不同插件的具体实现，这个例子实现了两个：

::

    import textwrap

    #from plugin import base
    import base


    class FieldList(base.FormatterBase):
        """Format values as a reStructuredText field list.

        For example::

          : name1 : value
          : name2 : value
          : name3 : a long value
              will be wrapped with
              a hanging indent
        """

        def format(self, data):
            """Format the data and return unicode text.

            :param data: A dictionary with string keys and simple types as
                         values.
            :type data: dict(str:?)
            """
            for name, value in sorted(data.items()):
                full_text = ': {name} : {value}'.format(
                    name=name,
                    value=value,
                )
                wrapped_text = textwrap.fill(
                    full_text,
                    initial_indent='',
                    subsequent_indent='    ',
                    width=self.max_width,
                )
                yield wrapped_text + '\n'
                
::

    #from plugin import base
    import base

    class Simple(base.FormatterBase):
        """A very basic formatter.
        """

        def format(self, data):
            """Format the data and return unicode text.

            :param data: A dictionary with string keys and simple types as
                         values.
            :type data: dict(str:?)
            """
            for name, value in sorted(data.items()):
                line = '{name} = {value}\n'.format(
                    name=name,
                    value=value,
                )
                yield line

**注意，Python源码中，可以直接import当前目录下的py文件，所以可以import base**

声明插件
=========

stevedore利用了pkg_resources的entry_points功能，声明插件，就是在setup.py中添加一条entry_points记录。

::

    from setuptools import setup, find_packages

    setup(
        name='stevedore-demo',
        version='0.1',

        packages=find_packages(),
        #include_package_data=True,

        entry_points={
            'stevedemo.formatter': [
                'simple = stevedemo.simple:Simple',
                'field = stevedemo.fields:FieldList',
                'plain = stevedemo.simple:Simple',
            ],
        },

        zip_safe=False,
    )


执行
=====

有两种方式执行，一种是根据name使用DriverManager加载执行某一个确定的插件：

::

    from __future__ import print_function

    import argparse

    from stevedore import driver


    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'format',
            nargs='?',
            default='simple',
            help='the output format',
        )
        parser.add_argument(
            '--width',
            default=60,
            type=int,
            help='maximum output width for text',
        )
        parsed_args = parser.parse_args()

        data = {
            'aaa': 'AAA',
            'bbb': 'BBB',
            'long': 'driver ' * 40,
        }

        mgr = driver.DriverManager(
            namespace='stevedemo.formatter',
            name=parsed_args.format,
            invoke_on_load=True,
            invoke_args=(parsed_args.width,),
        )
        for chunk in mgr.driver.format(data):
            print(chunk, end='')

另外一种是使用ExtensionManager加载执行某个命名空间下的所有插件：

::

    from __future__ import print_function

    import argparse
    from stevedore import extension

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--width',
            default=60,
            type=int,
            help='maximum output width for text',
        )
        parsed_args = parser.parse_args()

        data = {
            'abc': 'ABC',
            'b_extension': 'B_EXTENSION',
            'long': 'extension ' * 40,
        }

        mgr = extension.ExtensionManager(
            namespace='stevedemo.formatter',
            invoke_on_load=True,
            invoke_args=(parsed_args.width,),
        )

        def format_data(ext, data):
            return (ext.name, ext.obj.format(data))

        results = mgr.map(format_data, data)

        for name, result in results:
            print('Formatter: {0}'.format(name))
            for chunk in result:
                print(chunk, end='')
            print('=' * 40)


此时执行程序，代码并不能正确执行。

.. code-block:: console

    root@allinone-v2:/smbshare/stevedemo# python stevedemo/load_as_driver.py 
    Traceback (most recent call last):
      File "stevedemo/load_as_driver.py", line 34, in <module>
        invoke_args=(parsed_args.width,),
      File "/usr/lib/python2.7/dist-packages/stevedore/driver.py", line 45, in __init__
        verify_requirements=verify_requirements,
      File "/usr/lib/python2.7/dist-packages/stevedore/named.py", line 56, in __init__
        self._init_plugins(extensions)
      File "/usr/lib/python2.7/dist-packages/stevedore/driver.py", line 97, in _init_plugins
        (self.namespace, name))
    RuntimeError: No 'stevedemo.formatter' driver found, looking for 'simple'

需要先进行打包，然后就可以了。利用下面的命令，都可以！

.. code-block:: console

    #python setup.py develop
    #python setup.py install
    root@allinone-v2:/smbshare/stevedemo# python stevedemo/load_as_driver.py 
    aaa = AAA
    bbb = BBB
    long = driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver driver


---------------------

参考
=====

.. [#] https://pure-earth-7284.herokuapp.com/2015/05/16/OpenStack%E6%89%A9%E5%B1%95%E8%AE%BE%E8%AE%A1%E4%B9%8Bstevedore%E6%8F%92%E4%BB%B6/


