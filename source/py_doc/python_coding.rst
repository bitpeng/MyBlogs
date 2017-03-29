
####################
Python 编码问题总结
####################


注意：如没有特别说明，所有的描述均针对Python2.x。试验验证一般采用的Ubuntu-14.04-LTS Python2.7。

.. contents:: 目录

-----------------

Python蛋疼的编码问题，陆陆续续遇到过很多次了。原来在爬取网页时，
就遇到过网页乱码；最近测试wsgi程序时，又遇到 `AssertionError: write() argument must be string` 问题。
原来Python编码问题就做过相关总结，今天又探索了一番，记录下来，以作参考。

系统默认编码
============

Python2.x 中有多个不同的系统默认编码。

.. [#] https://gist.github.com/x7hub/178c87f323fbad57ff91

源文件编码
++++++++++

一般在源文件开头，通过指定：

::

    #coding:utf-8
    #coding=utf-8

来设置当源文件中有飞拉丁字符时的情况(如中文注释)。如果没有指定，系统就会默认使用ascii对源文件编码，会出现不能识别中文的情况。

sys.stdin.encoding和sys.stdout.encoding
+++++++++++++++++++++++++++++++++++++++

sdtin和stdout输入输出使用的编码，包括命令行参数和print输出，由locale环境变量决定。在en_US.UTF-8的系统中，默认值是UTF-8。

::

    >>> import sys
    >>> sys.stdin.encoding
    'UTF-8'
    >>> sys.stdout.encoding
    'UTF-8'
    >>> 

sys.getdefaultencoding()
+++++++++++++++++++++++++

**在Python2.x中：只有unicode对象才是真正意义的文本串，str类型表示的字节序列** 。Python2文本串和字节序列可以进行拼接、格式化等混合操作。混合操作过程不可编码的涉及到编码转换(Python解释器隐式进行)，因此Python2中，涉及到编码隐式转换的，都会使用sys.getdefaultencoding()进行.【参考stackoverflow，再加上个人理解！】

`sys.getdefaultencoding() is used on Python 2 for implicit conversions (when the encoding is not set explicitly) i.e., Python 2 may mix ascii-only bytestrings and Unicode strings together e.g., xml.etree.ElementTree stores text in ascii range as bytestrings or json.dumps() returns an ascii-only bytestring instead of Unicode in Python 2 — perhaps due to performance — bytes were cheaper than Unicode for representing ascii characters. Implicit conversions are forbidden in Python 3.`

.. [#] http://stackoverflow.com/questions/15530635/why-is-sys-getdefaultencoding-different-from-sys-stdout-encoding-and-how-does


文本串/字节串混合操作
=======================

前文提到，Python2.x中文本串(unicode对象)和字节串(str类型对象)可以混合操作。中间涉及到的编码隐式转换由Python解释器自动完成。

::

    >>> a = '<+ a:%s +> '
    >>> b = u'{b:%s} '
    >>> 
    >>> print type(a + b)
    <type 'unicode'>
    >>> print type(b + a)
    <type 'unicode'>
    >>> print type(a%b)
    <type 'unicode'>
    >>> print type(b%a)
    <type 'unicode'>
    >>> 

**可以看到，文本串和字节串混合操作时，一律都是str对象转换成unicode然后操作。结果类型也一律是unicode对象！**

假如混合操作时有非拉丁字母，会怎样呢？

::

    >>> sys.getdefaultencoding()
    'ascii'
    >>> a = '<+ 你好:%s +> '
    >>> b = u'{中国:%s} '
    >>> 
    >>> print type(a + b)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xe4 in position 3: ordinal not in range(128)
    >>> print a.decode('utf-8') + b
    <+ 你好:%s +> {中国:%s} 
    >>> print a + b.encode('utf-8')
    <+ 你好:%s +> {中国:%s} 
    >>> 
    >>> reload(sys)
    <module 'sys' (built-in)>
    >>> sys.setdefaultencoding('utf-8')
    >>> print type(a + b)
    <type 'unicode'>
    >>> print type(b%a)
    >>> a
    '<+ \xe4\xbd\xa0\xe5\xa5\xbd:%s +> '
    >>> 


不出意外，果然混合操作失败了。根据异常信息，可以看到，系统隐式转换时
尝试使用ascii对a字节序列进行编码。 ``\xe4`` 超出了ascii的编码范围，所以
编码转换失败。

通过 setdefaultencoding("utf-8")，后面的操作都成功了。但是，需要注意的是，该操作虽然可以解决中文乱码问题，但是也可能带来其他bug。要避免使用，我们Python项目中，也很少发现该用法。

.. [#] http://blog.ernest.me/post/python-setdefaultencoding-unicode-bytes

Python2.x中的string
===================

Python为了让其语法看上去简洁好用，做了很多tricky的事情，混淆byte string和text string就是其中一例。

在 Python 里，有三大类 string 类型：

-   unicode（text string），
-   str（byte string，二进制数据），
-   basestring，是前两者的父类。

其实，在语言设计领域，一串字节（sequences of bytes）是否应该当做字符串（string）一直是存在争议的。我们熟知的 Java 和 C# 投了反对票，而 Python 则站在了支持者的阵营里。其实我们在很多情况下，给文本做的操作，比如正则匹配、字符替换等，对于字节来说是用不着的。而 Python 认为字节就是字符，所以他们俩的操作集合是一致的。

然后进一步的，Python 会在必要的情况下，尝试对字节做自动类型转换，例如，在上文中的 ==，或者字节和文本拼接时。如果没有一个编码（encoding），两个不同类型之间的转换是无法进行的，于是，Python 需要一个默认编码。在 Python2 诞生的年代，ASCII 是最流行的（可以这么说吧），于是 Python2 选择了ASCII。然而，众所周知，在需要需要转换的场景，ASCII 都是没用的（128个字符，够什么吃）。

在历经这么多年吐槽后，Python 3 终于学乖了。默认编码是Unicode，这也就意味着，做所有需要转换的场合，都能正确并成功的转换。

最佳实践
=========

在Python2.x中，编码问题尽量遵循下列原则。

-   所有 text string 都应该是 unicode 类型，而不是 str，如果你在操作 text，而类型却是 str，那就是在制造 bug。

-   在需要转换的时候，显式转换。从字节解码成文本，用var.decode(encoding)，从文本编码成字节，用 var.encode(encoding)。

-   从外部读取数据时，默认它是字节，然后 decode 成需要的文本；同样的，当需要向外部发送文本时，encode 成字节再发送。


Python unicode HowTo
====================

该节的大部分内容，来源于Python官网Python HowTo,强烈推荐。英文看起来也一点都不难！

编码定义
++++++++

unicode定义了字符集和码点(code point)的映射，一个unicode string就是一系列unicode码点序列。该码点序列在计算机内存中需要有种表示方式，定义unicode string码点序列到内存字节序列的转换规则就称之为编码。

读写unicode数据
++++++++++++++++

一旦程序涉及到操作unicode 数据的代码，下一个问题就是I/O。你的程序从哪里获得unicode数据？怎样把unicode数据转换成合适的格式以供传输和存储？

根据你的数据输入源和输出目的地，有时你可能什么都不用做，你只需要检查你程序中所使用的库是否原声的支持unicode。比如XML解析库一般都直接返回unicode数据；许多关系数据库都支持unicode列存储和unicode SQL查询！

但是unicode数据写到磁盘上或者传送到socket时，一般都会转换成特定的格式。但是这时我们需要注意的是读取不完整unicode的问题。

WSGI/HTTP编码问题
=================

通常，http协议处理的是字节序列(HTTP 协议也不直接支持unicode，来源于PEP-3333)，因此，wsgi规范涉及到的string一般都是bytestring。近期测试webob程序的时候，程序总是报错。原来wsgi app要求假如返回字符串类型，则只能是str类型，而不能是unicode类型。

::

    def simple_app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type','text/plain')]
        start_response(status, response_headers)
        # app 的返回值不能是 unicode 对象！
        return [u'Hello world!\n']
        #return ['Hello world!\n']

simple_app返回的可迭代对象元素是unicode类型，因此curl请求时，报错如下:

::

        assert type(data) is StringType,"write() argument must be string"
    AssertionError: write() argument must be string
    127.0.0.1 - - [20/Nov/2016 20:24:40] "GET / HTTP/1.1" 500 59

请看pep-3333 wsgi规范关于unicode 的描述：

HTTP does not directly support Unicode, and neither does this interface. All encoding/decoding must be handled by the application; all strings passed to or from the server must be of type str or bytes , never unicode . The result of using a unicode object where a string object is required, is undefined.

HTTP协议不直接支持unicode，它的接口也不支持。因此app需要处理encoding/decoding：所有的strings(server传来的和传递给server的)都只能是str类型或者bytes类型，决不能是unicode。在需要string对象而返回unicode对象的地方，结果是未定义的！

Note also that strings passed to start_response() as a status or as response headers must follow RFC 2616 with respect to encoding. That is, they must either be ISO-8859-1 characters, or use RFC 2047 MIME encoding.

同样需要指出：传递给 start_response 回调函数的strings(作为HTTP 响应状态码和头部)需要服从RFC-2616的编码规定。因此：他们只可能是ISO-8859-1字符集或者RFC-2047多媒体编码！

On Python platforms where the str or StringType type is in fact Unicode-based (e.g. Jython, IronPython, Python 3, etc.), all "strings" referred to in this specification must contain only code points representable in ISO-8859-1 encoding ( \u0000 through \u00FF , inclusive). It is a fatal error for an application to supply strings containing any other Unicode character or code point. Similarly, servers and gateways must not supply strings to an application containing any other Unicode characters.

在python平台上，str和StringType类型都是基于unicode的(如：Jython, IronPython, Python3);该规范里涉及到的所有strings只能包含 ISO-8859-1编码规则列出的码点。wsgi app 提供包含任意其他unicode字符集或者码点的strings都是严重错误。类似的，servers或者gateway也不应该给一个app提供包含其他unicode字符集的strings

Again, all objects referred to in this specification as "strings" must be of type str or StringType , and must not be of type unicode or UnicodeType . And, even if a given platform allows for more than 8 bits per character in str / StringType objects, only the lower 8 bits may be used, for any value referred to in this specification as a "string".

再次强调：该规范里涉及的所有string对象只能是str或者StringType，而不能是unicode 或者UnicodeType；即使有些平台str或者StringType对象支持超过 8bits/每字符，也可能只有低8位字符可用。

For values referred to in this specification as "bytestrings" (i.e., values read from wsgi.input , passed to write() or yielded by the application), the value must be of type bytes under Python 3, and str in earlier versions of Python.

如果该规范里涉及到的值为”bytestrings“(如：wsgi.input, 传递给write(),或者由app yield产生)，他们的类型只能是bytes(在Python3中)，或者str(以前的Python版本！) 


-------------

参考
=====

.. [#] http://pycoders-weekly-chinese.readthedocs.io/en/latest/issue5/unipain.html
.. [#] http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001431664106267f12e9bef7ee14cf6a8776a479bdec9b9000
.. [#] http://www.ituring.com.cn/article/1116
.. [#] https://www.python.org/dev/peps/pep-3333/#unicode-issues
