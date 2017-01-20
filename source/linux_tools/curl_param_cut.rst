.. _curl_param_cut:


########################
shell 元字符问题
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^




--------------------------

curl 命令行参数截断问题
========================

在使用curl 测试paste库的过程中，发现总是出现错误：

curl 请求及输出如下：

.. code-block:: console

    root@juno-controller:/# curl http://localhost:9999/calc?oper=plus&op1=20&op2=30
    [1] 10390
    [2] 10391
    root@juno-controller:/# A server error occurred.  Please contact the administrator.
    [1]-  Done                    curl http://localhost:9999/calc?oper=plus
    [2]+  Done                    op1=20

通过查看服务端程序输出，发现只有plus参数成功专递，后面的op1和op2两个参数不见了。

.. figure:: /_static/images/curl_error.png
   :scale: 100
   :align: center

   curl 参数截断

原来，&字符是shell的元字符，被shell解释了。根本没有传递给curl程序！因此，我们使用反斜杠对&进行转义即可！
现在传递的参数也正常了。

.. code-block:: console

    root@juno-controller:/# curl http://localhost:9999/calc?oper=plus\&op1=20\&op2=30
    GET([(u'oper', u'plus'), (u'op1', u'20'), (u'op2', u'30')]) 
    RESULT = 50

.. figure:: /_static/images/curl_ok.png
   :scale: 100
   :align: center


引号
====

先来看看原来编写lvm自动化脚本遇到的问题：

.. code:: shell

    vgdisplay| grep "VG Name" | awk "{print $3}"
    #  VG Name               juno-controller-vg
    vgdisplay| grep "VG Name" | awk '{print $3}'
    #juno-controller-vg

上面的命令，是想取得系统的LVM逻辑卷组，但是，我们可以看到，第一条命令才是正确的。
这里涉及到单双引号关闭元字符的问题。

- hard quote：单引号，关闭所有的meta（什么是meta，自己查吧）
- soft quote：双引号，关闭大部分的meta，但是某些保留，例如$

这里也提一下escape：反斜杠，它只会关闭紧跟escape之后的字符。

参考cu上经典的十三问，hard quote关闭shell的meta，而soft quote关闭大部分的shell meta，但是$例外，对于bash的来说，命令的解释是从左到右的，首先遇到hard quote和soft quote，所作的解释是不一样，看这个例子：


.. figure:: /_static/images/quote_test.png
   :scale: 100
   :align: center

   单双引号区别测试

.. code-block:: console

    root@juno-controller:/# a=1
    root@juno-controller:/# echo "$a"    #$被bash解释到
    1
    root@juno-controller:/# echo '$a'    #$被hard quote被关闭
    $a
    root@juno-controller:/# echo '"$a"'  #$被hard quote关闭
    "$a"
    root@juno-controller:/# echo "'$a'"  #所有都被关闭了
    '1'


如果能够理解上面的了，那基本知道怎么用单引号和双引号了。

而对于awk、ed等等命令，需要区分shell meta和command meta
对于awk来说，它的{ }：是将其内的命令置于non-named function 中执行，awk用{ }来区分命令段，例如BEGIN，END等等。举个例子：

.. code-block:: console

    root@ubuntu:/# head -4 /etc/passwd | awk -F: {print $1}
    awk: line 2: missing } near end of file

看看报错，如果直接使用{ }，那么我们知道{ }没有被shell关闭，也就是说它看成shell的meta了，当然报错了，所以要关闭，同时shell中的$也关闭，也就是$需要成为awk的meta了，很好理解吧？如下输出了内容。

.. code-block:: console

    root@ubuntu:/# head -4 /etc/passwd | awk -F: '{print $1}'
    root
    daemon
    bin
    sys


既然要要关闭{ }，那么也可以用soft quote，

.. code-block:: console

    root@ubuntu:/# head -4 /etc/passwd | awk -F: "{print $1}"
    root:x:0:0:root:/root:/bin/bash
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    sys:x:3:3:sys:/dev:/usr/sbin/nologin


可以看到，soft quote预期的关闭了{ }，但是$还是被shell解释了，这次我们可以用escape，将$关闭了。

.. code-block:: console

    root@ubuntu:/# head -4 /etc/passwd | awk -F: "{print \$1}"
    root
    daemon
    bin
    sys


说到这里，可以大家都一点明白了，并不是awk '{ }' urfile是awk的固定语法，而是为了让awk能够跳脱shell的偷取其命令和参数，看看这个例子就明白了。

.. code-block:: console

    root@ubuntu:/# head -4 /etc/passwd | awk -F: \{print\ \$1}
    root
    daemon
    bin
    sys


所作的一切是为了让awk或者自己的meta，请切记注意print后的空格，也要关闭，要不又被shell解释了。

**总结**

-   双引号作用与单引号类似，区别在于它没有那么严格。单引号告诉shell
    忽略所有特殊字符，而双引号只要求忽略大多数，具体说，括在双引号
    中的三种特殊字符不被忽略：$,\,` ,即双引号会解释字符串的特别意思,
    而单引号直接使用字符串.

-   反斜杠backslash-escaped( \ )一般用作转义字符,或称逃脱字符,
    linux如果echo要让转义字符发生作用,就要使用-e选项,且转义字符要使
    用双引号echo -e "\n"反斜杠的另一种作用,就是当反斜杠用于一行的
    最后一个字符时，shell把行尾的反斜杠作为续行，
    这种结构在分几行输入长命令时经常使用。

-   *$()和``的区别* ：反引号和$()的功能是命令替换，将反引号或$()中的字符串做为命令来执行，
    我们在用shell编程时经常用的到　将系统命令的执行结果赋给一个变量
    但反引号内不能再引用反引号，而$()中可以引用反引号

