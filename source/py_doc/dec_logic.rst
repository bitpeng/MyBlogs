.. _dec_logic:


########################
Python 装饰器、闭包
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. contents:: 目录

--------------------------

Python 闭包
===========

首先来看看维基百科对闭包的定义：

.. tip::

    在一些语言中，在函数中可以（嵌套）定义另一个函数时，如果内部的函数引用了外部的函数的变量，
    则可能产生闭包。运行时，一旦外部的 函数被执行，一个闭包就形成了，
    闭包中包含了内部函数的代码，以及所需外部函数中的变量的引用。
    
    闭包可以用来在一个函数与一组“私有”变量之间创建关联关系。
    **在给定函数被多次调用的过程中，这些私有变量能够保持其持久性。**

注意，Python闭包必须通过嵌套函数定义实现，但是嵌套函数不一定是闭包，StackOverflow上有对两者的
区别做了清晰的阐述！

当一个函数在执行完后，访问了嵌套作用域的局部变量，闭包就产生了。

::

    def make_printer(msg):
        def printer():
            print msg
        return printer

    printer = make_printer('Foo!')
    printer()


当 ``make_printer`` 被调用后，一个新的带有编译过的字节码函数frame在栈上生成，并
有msg局部变量。因为 ``printer`` 函数引用了msg 变量，因此msg在 ``make_printer`` 调用后
一直存在！

因此，假如嵌套函数没有访问嵌套作用域的局部变量，它就不是闭包.

::

    def make_printer(msg):
        def printer(msg=msg):
            print msg
        return printer

    printer = make_printer("Foo!")
    printer()  #Output: Foo!
    
在该例子中，msg只是给 ``printer`` 函数提供默认参数，是 ``printer`` 的一个局部
变量，因此不是闭包！

总结，产生闭包必须具备三个条件：

- 需要定义嵌套函数；
- 嵌套函数需要引用enclosing function中的变量；
- enclosing function需要返回嵌套函数；

.. [#] http://stackoverflow.com/questions/4020419/why-arent-python-nested-functions-called-closures
.. [#] https://www.programiz.com/python-programming/closure
.. [#] http://python.jobbole.com/82624/


Python 装饰器
=============

函数是对象
++++++++++

理解装饰器，你首先需要注意到，在Python中函数也是对象，这非常重要。

::

    def shout(word="yes"):
        return word.capitalize()+"!"

    print(shout())
    # outputs : 'Yes!'

    # As an object, you can assign the function to a variable like any other object 
    scream = shout

    # Notice we don't use parentheses: we are not calling the function, we are putting the function "shout" into the variable "scream". It means you can then call "shout" from "scream":

    print(scream())
    # outputs : 'Yes!'

    # More than that, it means you can remove the old name 'shout', and the function will still be accessible from 'scream'

    del shout
    try:
        print(shout())
    except NameError, e:
        print(e)
        #outputs: "name 'shout' is not defined"

    print(scream())
    # outputs: 'Yes!'
    
另外一个有趣特性是，可以在函数内部再定义函数：

::

    def talk():

        # You can define a function on the fly in "talk" ...
        def whisper(word="yes"):
            return word.lower()+"..."

        # ... and use it right away!
        print(whisper())

    # You call "talk", that defines "whisper" EVERY TIME you call it, then
    # "whisper" is called in "talk". 
    talk()
    # outputs: 
    # "yes..."

    # But "whisper" DOES NOT EXIST outside "talk":

    try:
        print(whisper())
    except NameError, e:
        print(e)
        #outputs : "name 'whisper' is not defined"*
        #Python's functions are objects

函数引用
++++++++

由于函数是对象，因此：

- 函数可以赋值给另外一个变量；
- 函数可以在另外一个函数内部中定义；
- **一个函数可以返回另外一个函数**；
- 把函数当做参数传递；

好了，现在可以讲装饰器了，**装饰器是一种“包装”，允许在被包装函数运行之前、运行之后
执行代码，并且不更改被包装的函数！**

手动装饰器
++++++++++

::

    # A decorator is a function that expects ANOTHER function as parameter
    def my_shiny_new_decorator(a_function_to_decorate):

        # Inside, the decorator defines a function on the fly: the wrapper.
        # This function is going to be wrapped around the original function
        # so it can execute code before and after it.
        def the_wrapper_around_the_original_function():

            # Put here the code you want to be executed BEFORE the original function is called
            print("Before the function runs")

            # Call the function here (using parentheses)
            a_function_to_decorate()

            # Put here the code you want to be executed AFTER the original function is called
            print("After the function runs")

        # At this point, "a_function_to_decorate" HAS NEVER BEEN EXECUTED.
        # We return the wrapper function we have just created.
        # The wrapper contains the function and the code to execute before and after. It’s ready to use!
        return the_wrapper_around_the_original_function

    # Now imagine you create a function you don't want to ever touch again.
    def a_stand_alone_function():
        print("I am a stand alone function, don't you dare modify me")

    a_stand_alone_function() 
    #outputs: I am a stand alone function, don't you dare modify me

    # Well, you can decorate it to extend its behavior.
    # Just pass it to the decorator, it will wrap it dynamically in 
    # any code you want and return you a new function ready to be used:

    a_stand_alone_function_decorated = my_shiny_new_decorator(a_stand_alone_function)
    a_stand_alone_function_decorated()
    #outputs:
    #Before the function runs
    #I am a stand alone function, don't you dare modify me
    #After the function runs

未完待续……

.. [#] http://stackoverflow.com/questions/739654/how-to-make-a-chain-of-function-decorators-in-python


装饰器逻辑
===========

Python装饰器可以理解，可是每次阅读代码时，都要使用转换过的方法才能顺着看。
因此这里作以下总结。以方便快速阅读代码

类装饰器
++++++++

::

    # 类装饰器
    @webob.dec.wsgify
    def app1(req):
        return webob.Response("Hello, app1")

类似于：

::

    app1_obj = wsgify(app1)

为了描述方便，将原始的定义的方法称为app1, 包装后返回的对象称为
app1_obj, 包装后，app1为类对象，因此wsgify 类一定定义了__call__方法。
调用app1_obj(……)时，实际上是先调用__call__ 方法，然后一般在
__call__方法中再次调用原始的函数(app1函数)！


函数装饰器
++++++++++

::

    # 函数装饰器
    def dec_func1(path):
        '''
        A @get decorator.

        @get('/:id')
        def index(id):
            pass
        '''
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'GET'
            return func
        return _decorator

    @dec_func1('/:id')
    def app2(id):
        pass

调用逻辑类似于：

::

    app2_func = dec_func1(app2)

这种情况, dec_func1一定定义了闭包。
app2_func实际上是内层闭包函数(这里是_decorator函数)，因此调用
app2_func(……)相当于执行内层闭包函数！



类装饰器带参数
++++++++++++++

::

    # 类装饰器
    @webob.dec.wsgify(RequestClass=webob.Request)
    def app3(req):
        return webob.Response("Hello, app1")

类似于:

::

    app3_obj = wsgify(RequestClass=webob.Request)(app3)

再类似于：

::

    wsgify_obj = wsgify(RequestClass=webob.Request)
    app3_obj = wsgify_obj(app3)

这种情况，要求wsgify定义了__call__方法，并且wsgify_obj(app3)
的执行结果一般应该返回一个可调用对象。

