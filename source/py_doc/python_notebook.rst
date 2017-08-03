###################
Python学习总结
###################



.. tip::
    这是自己学习Python和工作中的总结，包括Python语言特性，小技巧，
    编程中容易出现的陷阱；以及常用的标准库和第三方库。

.. contents:: 目录


--------------

语言特性
===================

str
~~~~

partition和rpartition
^^^^^^^^^^^^^^^^^^^^^^

::

    >>> s="nova.scheduler.manager.SchedulerManager"
    >>> s.rpartition('.')
    ('nova.scheduler.manager', '.', 'SchedulerManager')
    >>> s.partition('.')
    ('nova', '.', 'scheduler.manager.SchedulerManager')


startswith
^^^^^^^^^^

::

    s = "ceil-meter"
    s.startswith("ceil")

format
^^^^^^^^^

::

    >>> msg = "hello, {name}. This is {lan}"
    >>> msg
    'hello, {name}. This is {lan}'
    >>> msg.format(name="chenshiqiang", lan="python")
    'hello, chenshiqiang. This is python'



dict
~~~~~~~~

fromkeys()方法：
^^^^^^^^^^^^^^^^^^^^

.. code:: python

    >>> s = [1,2,3]
    >>> dict.fromkeys(s)
    {1: None, 2: None, 3: None}
    >>> v = {'a', 'b'}
    >>> dict.fromkeys(s,v)
    {1: set(['a', 'b']), 2: set(['a', 'b']), 3: set(['a', 'b'])}
    >>> v = {'a', 'b', 'a'}
    >>> dict.fromkeys(s,v)
    {1: set(['a', 'b']), 2: set(['a', 'b']), 3: set(['a', 'b'])}
    >>> 

pop()方法
^^^^^^^^^^^^^^

dict.pop(key [,default]): 如果key存在，删除并返回dict[key];
如果key不存在，default存在，返回default；如果default也不存在，KeyError异常。

update()
^^^^^^^^^^^^

golbal
~~~~~~~~~~

and/or/not
~~~~~~~~~~~

.. code:: python

    # and表达式都是真时，返回第二个；都是假时返回第一个；一真一假时返回假的。
    >>> 'a' and 'b'
    'b'
    >>> 'b' and 'a'
    'a'
    >>> '' and False
    ''
    >>> False and ''
    False
    >>> '' and 'a'
    ''
    >>> 'a' and ''
    ''
    >>> 
    # or表达式都是真时返回第一个；都是假如返回第二个；一真一假返回真的。
    >>> 'a' or 'b'
    'a'
    >>> 'b' or 'a'
    'b'
    >>> '' or False
    False
    >>> False or ''
    ''
    >>> '' or 'a'
    'a'
    >>> 'a' or ''
    'a'
    >>>

    # 从这里的测试可以，可以看到，not的优先级高于and和or
    >>> not 0 and 0
    0
    >>> not 0 and 1
    1
    >>> not 1 and 0
    False
    >>> not 1 and 1
    False
    >>>

    >>> not 0 or 0
    True
    >>> not 0 or 1
    True
    >>> not 1 or 0
    0
    >>> not 1 or 1
    1
    >>>



for……else循环
~~~~~~~~~~~~~~~~~

在for循环完整完成后才执行else；如果中途从break跳出，则连else一起跳出。

默认参数问题
~~~~~~~~~~~~~~~~

请看代码：

.. code:: python

    >>> def f(x = []):
        print(id(x))
        x.append(1)
        print(id(x))

        
    >>> f() 
    38869952  # 可变默认参数是在原地更改！！！
    38869952
    >>> f()
    38869952  # 再次调用时，可变默认参数还是引用最初定义的！！！
    38869952
    # 注意，默认参数是在定义时赋值，且仅仅赋值一次。
    # 当函数多次被调用，并且没有提供默认的参数值，就会从定义时赋值的地方取得值！
    # 即使函数中给默认参数重新赋值了，下次调用还是会从定义赋值的地方取得值！
    # 如以下的示例：当f2()多次调用，虽然在函数体里面给y重新赋值了，但是下次调用时
    # 再次打印print id(x) 的结果也还是一样的！
    # 所以：
    # 1. 假如默认参数是可变对象，则会在原处直接更改对象，下次调用参数时，默认参数已经
    #    更改过的了。如f()函数。
    # 2. 假如默认参数不可变，那么给函数中给 参数赋值时，参数会引用内存的其他地方。下次函数调用时
    #    默认参数还是从定义时赋值处取得值，因为没有副作用！
    >>> def f2(y = None):
        print(id(y))
        if not y:
            y = []
        y.append(1)
        print(id(y))

        
    >>> f2()
    505672708   # 定义时默认参数引用这一块内存。
    38888872    # 函数体内赋值后，y引用其他地方。
    >>> f2()
    505672708   # 再次调用，y还是引用定义时赋值的内存处。
    43910728    # 函数体内赋值后，y引用其他地方。
    >>> f()
    38869952    
    38869952
    >>> f2()
    505672708
    43909408
    >>> f2()
    505672708
    38868752
    >>> 

getattr, hasattr, setattr
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**用法**\ ：

-  getattr
   如果存在name属性（方法）则返回name的值（方法地址）,否则返回default值;
-  hasattr 可以用来判断object中是否具有name属性;
-  setattr(object, name, value)类似于object.name = value;

.. code:: python

    >>> class A:
    ...     def __init__(self):   
    ...         self.name = 'zhangjing'  
    ...         #self.age='24'
    ...     def method(self):   
    ...         print"method print"
    ... 
    >>> 
    >>> a = A()
    >>> m = getattr(a, 'method', 'default')
    >>> um = getattr(a, 'undef', 'default')
    >>> m
    <bound method A.method of <__main__.A instance at 0xb728d9ac>>
    >>> um
    'default'
    >>> m()
    method print
    >>> hasattr(m, 'method')
    False
    >>> hasattr(a, 'method')
    True
    >>> hasattr(A, 'method')
    True
    >>> unbf = getattr(A, 'method')
    >>> unbf
    <unbound method A.method>

callable
~~~~~~~~~~~~

原始字符串
~~~~~~~~~~~~~~

原始类型字符串可以简单的通过在普通字符串的双引号前面加一个字符‘r’来创建。当一个字符串是原始类型时，Python编译器不会对其尝试做任何的替换。本质上来讲，你在告诉编译器完全不要去干涉你的字符串。

.. code:: python

    >>> string = 'This is a\nnormal string'
    >>> rawString = r'and this is a\nraw string'
    >>> print string
    #这是一个普通字符串
    >>> print rawString
    and this is a\nraw string
    #这是一个原始类型字符串。

语言陷阱
===================

浅复制
~~~~~~~~~~

**关于Python列表赋值，特别需要注意的一点：**

.. code:: python

    #通过这个例子，看到了，用a=a=[[]]*4形式生产的列表，所有的id号都是
    #一样的，引用的是同一个元素！
    >>> a=[[]]*4
    >>> a
    [[], [], [], []]
    >>> for i in range(4):
        print (id(a[i]))

        
    38964480
    38964480
    38964480
    38964480
    #而通过append方式插入的元素，都是不想关的，不是同一个元素！
    >>> a = []
    >>> for i in range(4):
        a.append([])

        
    >>> a
    [[], [], [], []]
    >>> for i in range(4):
        print (id(a[i]))
        
    38964160
    38964000
    38960384
    38965120
    >>>

小技巧
===================

获取函数名，当前行号，文件名
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  方法一：

   .. code:: python

       print sys._getframe().f_code.co_filename  #当前文件名，也可以通过__file__获得
       print sys._getframe().f_code.co_name  #当前函数名
       print sys._getframe().f_lineno #当前行号

-  方法二：

   .. code:: python

       def get_cur_info():
           """Return the frame object for the caller's stack frame."""
           try:
               raise Exception
           except:
               f = sys.exc_info()[2].tb_frame.f_back
           co_filename = f.f_code.co_filename
           co_filename = os.path.abspath(co_filename)
           #return (__file__, f.f_code.co_filename, f.f_code.co_name, f.f_lineno)
           return (co_filename, f.f_code.co_name, f.f_lineno)



标准库
===================

Httplib：http处理
~~~~~~~~~~~~~~~~~~~~~

自定义http请求头部
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    import httplib
    try:
        # simplejson is popular and pretty good
        from simplejson import loads as json_loads
        from simplejson import dumps as json_dumps
    except ImportError:
        # 2.6 will have a json module in the stdlib
        from json import loads as json_loads
        from json import dumps as json_dumps

    def test_httplib():
        # 自定义http请求头部字段
        header = {"X-Auth-Token":"c83cd8ba4f8ea2e67411", 'Content-Type':'application/json'}
        httpClient = httplib.HTTPConnection('192.168.218.131', 5000, timeout=30)
        httpClient.request('GET', '/v2.0/tokens/5811f83601524f20a50df6023df8f9c6', headers=header)

        #resp是HTTPResponse对象
        resp = httpClient.getresponse()
        body = resp.read()
        print resp.status, resp.reason, body

    if __name__ == "__main__":
        test_httplib()

ConfigParser：配置文件操作
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**作用**\ ：用来操作配置文件 比如有如下配置文件glusterrest.ini,
和Python源码放在同一目录下。

.. code:: shell

    [keystone_auth_config]
    admin_token=c83cd8ba4f8ea2e67411
    controller=192.168.218.131
    port=5000
    [mysql_db_config]
    host=localhost
    user=root
    passwd=root
    db=glusterrest

读取配置文件的程序：

.. code:: python

    # -*- coding: utf-8 -*-

    import ConfigParser
    import os

    def _config_file_path():
        # 取得文件的绝对路径
        abs_path = os.path.abspath(__file__)
        name = ["glusterrest.ini"]
        return '/'.join(abs_path.split("/")[:-1] + name)

    def get_keystone_auth_config():
        config_file = _config_file_path()
        cf = ConfigParser.ConfigParser()
        cf.read(config_file)
        #s = cf.sections()
        #print 'section:', s
        #o = cf.options("baseconf")
        #print 'options:', o
        #v = cf.items("baseconf")
        #print 'db:', v
        admin_token = cf.get("keystone_auth_config", "admin_token")
        controller = cf.get("keystone_auth_config", "controller")
        port = cf.get("keystone_auth_config", "port")
        #db_pwd = cf.get("baseconf", "password")
        #print db_host, db_port, db_user, db_pwd
        #cf.set("baseconf", "db_pass", "123456")
        #cf.write(open("config_file_path", "w"))
        return admin_token, controller, port

    if __name__ == "__main__":
        print get_keystone_auth_config()

re：正则匹配
~~~~~~~~~~~~~~~~

该部分可以使用一个专门的教程来讲述。请参考另一份笔记 :ref:`Python正则表达式 <py-regex-doc>`  。

Pexpect：自动化交互
~~~~~~~~~~~~~~~~~~~~~~~

Subprocess：创建进程
~~~~~~~~~~~~~~~~~~~~~~~~

functools
~~~~~~~~~~~~~

wraps
^^^^^^^^^

    If using a decorator always meant losing this information about a
    function, it would be a serious problem. That's why we have
    functools.wraps. This takes a function used in a decorator and adds
    the functionality of copying over the function name, docstring,
    arguments list, etc. And since wraps is itself a decorator, the
    following code does the correct thing:

.. code:: python

    from functools import wraps
    def logged(func):
        @wraps(func)
        def with_logging(*args, **kwargs):
            print func.__name__ + " was called"
            return func(*args, **kwargs)
        return with_logging

    @logged
    def f(x):
       """does some math"""
       return x + x * x

    print f.__name__  # prints 'f'
    print f.__doc__   # prints 'does some math'

还可以尝试进一步运行这个例子：

.. code:: python

    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    from functools import wraps

    def test():
        """function test doc string"""
        pass

    def my_decorator(f):
         #@wraps(f)
         #@wraps(f)
         @wraps(test)
         def wrapper(*args, **kwds):
             """wraps doc"""
             print 'Calling decorated function'
             return f(*args, **kwds)
         return wrapper

    @my_decorator
    def example():
        """这里是文档注释"""
        print 'Called example function'

    #example()
    print example.__name__ # 'example'
    print example.__doc__ # '这里是文档注释'

下面是这个例子的输出结果：

::

    root@ceph-deploy:/smbshare/pypro# python warps-test.py 
    wrapper
    wraps doc
    root@ceph-deploy:/smbshare/pypro# python warps-test.py 
    example
    这里是文档注释
    root@ceph-deploy:/smbshare/pypro# python warps-test.py 
    test
    function test doc string

update\_wrapper
^^^^^^^^^^^^^^^^^^^

功能： 用被包装函数的module,
name，doc和dict属性更新包装函数的相应部分，并返回包装函数。
以下是update\_wraps函数的实现代码：

.. code:: python

    WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__doc__')
    WRAPPER_UPDATES = ('__dict__',)
    def update_wrapper(wrapper,
                       wrapped,
                       assigned = WRAPPER_ASSIGNMENTS,
                       updated = WRAPPER_UPDATES):
        for attr in assigned:
            setattr(wrapper, attr, getattr(wrapped, attr))
        for attr in updated:
            getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
        return wrapper

ElementTree：XML解析
~~~~~~~~~~~~~~~~~~~~~~~~

假设有如下xml文件（完整的xml文件为360云盘上的\ ``volinfo.xml``\ ）：

.. code:: xml

    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <cliOutput>
      <opRet>0</opRet>
      <opErrno>0</opErrno>
      <opErrstr/>
      <volInfo>
        <volumes>
          <volume>
            <name>dist-vol</name>
            <id>ffe97ef8-7ab9-41ab-a43b-8b8c7816cf78</id>
            <status>1</status>
            <statusStr>Started</statusStr>
            <brickCount>3</brickCount>
            <distCount>1</distCount>
            <stripeCount>1</stripeCount>
            <replicaCount>1</replicaCount>
            <disperseCount>0</disperseCount>
            <redundancyCount>0</redundancyCount>
            <type>0</type>
            <typeStr>Distribute</typeStr>
            <transport>0</transport>
            <bricks>
              <brick uuid="0a3efc15-3358-43a2-b503-1e67d6eeea02">ubuntu1:/gfs-dir/dist-dir<name>ubuntu1:/gfs-dir/dist-dir</name><hostUuid>0a3efc15-3358-43a2-b503-1e67d6eeea02</hostUuid></brick>
              <brick uuid="05c9c42b-e4c9-4016-8280-32721bae6703">ubuntu2:/gfs-dir/dist-dir<name>ubuntu2:/gfs-dir/dist-dir</name><hostUuid>05c9c42b-e4c9-4016-8280-32721bae6703</hostUuid></brick>
              <brick uuid="05c9c42b-e4c9-4016-8280-32721bae6703">ubuntu2:/gfs-dir/addbrick-dir<name>ubuntu2:/gfs-dir/addbrick-dir</name><hostUuid>05c9c42b-e4c9-4016-8280-32721bae6703</hostUuid></brick>
            </bricks>
            <optCount>3</optCount>
            <options>
              <option>
                <name>features.quota</name>
                <value>on</value>
              </option>
              <option>
                <name>diagnostics.latency-measurement</name>
                <value>on</value>
              </option>
              <option>
                <name>diagnostics.count-fop-hits</name>
                <value>on</value>
              </option>
            </options>
          </volume>
          <count>3</count>
        </volumes>
      </volInfo>
    </cliOutput>

操作该文件的Python程序如下：

.. code:: python

    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    import xml.etree.cElementTree as etree
    import os


    def _read_xml_file():
        _abs_path = os.path.abspath(__file__)
        _name = ["volinfo.xml"]
        _p = '/'.join(_abs_path.split("/")[:-1] + _name)
        _xml_text = open(_p).read()
        return _xml_text


    def _parse_a_vol(volume_el):
        value = {
            'name': volume_el.find('name').text,
            'uuid': volume_el.find('id').text,
            'type': volume_el.find('typeStr').text.upper().replace('-', '_'),
            'status': volume_el.find('statusStr').text.upper(),
            'num_bricks': int(volume_el.find('brickCount').text),
            'distribute': int(volume_el.find('distCount').text),
            'stripe': int(volume_el.find('stripeCount').text),
            'replica': int(volume_el.find('replicaCount').text),
            'transport': volume_el.find('transport').text,
            'bricks': [],
            'options': []
        }
        if value['transport'] == '0':
            value['transport'] = 'TCP'
        elif value['transport'] == '1':
            value['transport'] = 'RDMA'
        else:
            value['transport'] = 'TCP,RDMA'

        for b in volume_el.findall('bricks/brick'):
            try:
                value['bricks'].append({"name": b.find("name").text,
                                        "hostUuid": b.find("hostUuid").text})
            except AttributeError:
                value['bricks'].append(b.text)

        for o in volume_el.findall('options/option'):
            value['options'].append({"name": o.find('name').text,
                                     "value": o.find('value').text})

        return value
        

    def test_xml():
        xmldata = _read_xml_file()
        #print xmldata
        tree = etree.fromstring(xmldata)
        
        volumes = []
        for el in tree.findall('volInfo/volumes/volume'):
            try:
                volumes.append(_parse_a_vol(el))
            except (ParseError, AttributeError, ValueError) as e:
                raise GlusterCliBadXml(str(e))

        return volumes


    if __name__ == "__main__":
        print test_xml()   

具体这个例子可以参考github上的\ ``glusterfs-rest``\ 项目

第三方库
=================

Flask框架
~~~~~~~~~~~~~

FireFox RESTclient插件发送POST请求和参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

如果想发送post请求：

    -  You have to set the “request header” section of the Firefox
       plugin to have a “name” = “Content-Type” and “value” =
       “application/x-www-form-urlencoded”
    -  Now, you are able to submit parameter like
       “name=mynamehere&title=TA” in the “request body” text area field

**参考**\ ：http://stackoverflow.com/questions/13132794/firefox-add-on-restclient-how-to-input-post-parameters

Flask框架获取HTTP headers字段
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

使用如下方法即可：

.. code:: python

    from flask import request
    token = request.headers.get('X-Auth-Token')

