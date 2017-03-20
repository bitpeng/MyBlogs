.. _iptables_sum:


########################
iptables 学习总结
########################

**date: 2017-02-17 10:30**

.. contents:: 目录

--------------------------


近期调研neutron-metering-agent组件，需要事先熟悉下iptables，把自己学习iptables的相关知识点记录下来，以供参考。


基本原理
=========

iptables是一个包过滤防火墙，依赖于内核模块netfilter，它根据数据包在Linux TCP/IP内核协议栈中的流动，选取了5个HOOK点，然后数据包依次经过5个HOOK点中的一个或者多个时，根据所预定义的规则进行数据包的匹配并执行相应的动作。iptables就是这样的用户层工具，允许我们自定义匹配规则。请看下面的相关概念：

表
++++

iptables根据功能分类，内置有几种不同的表，用来实现数据包过滤(filter)、网络地址转换(nat)、数据包修改(mangle)等。

链和规则
+++++++++

每个表都内置一组链，此外还允许用户自定义链。

.. figure:: /_static/images/iptables_chains.png
   :scale: 100
   :align: center

   iptables链

有关链和规则，有几点需要特别注意：

- 定义链的默认策略非常重要，因为假如数据包不符合链中任一规则，则会用默认策略进行处理；
- 由于数据包是依次使用链中规则进行匹配，因此规则的顺序也非常之重要。

数据包匹配流程
+++++++++++++++

关于数据包在iptables中经过的表/链的匹配流程，请看下面的图：

.. figure:: /_static/images/iptables_process.jpg
   :scale: 100
   :align: center

   iptables表/链匹配流程

.. figure:: /_static/images/tables_traverse.jpg
   :scale: 100
   :align: center

   匹配时依次经过的表/链

**由于个人主机一般不会开启IP转发功能，因此数据包主要涉及到的表是filter表，链是INPUT链。**
   
命令格式
=========

iptables操作规则的命令格式如下：

.. code-block:: sh

    iptables [-t 表名] <-A/I/D/R> 规则链名 [规则号] \
             <-i/o 网卡名> -p 协议名 <-s 源IP/源子网> \
             --sport 源端口 <-d 目标IP/目标子网> --dport 目标端口 \
             [-m 扩展模块 匹配条件]
             -j 动作

.. [#] http://man.linuxde.net/iptables

其中， **表名包括：**

- raw：高级功能，如：网址过滤。
- mangle：数据包修改（QOS），用于实现服务质量。
- net：地址转换，用于网关路由器。
- filter：包过滤，用于防火墙规则。

*假如表名没有指定的话，则默认是filter*

**规则链包括：**

- INPUT链：处理输入数据包；
- OUTPUT链：处理输出数据包；
- PORWARD链：处理转发数据包；
- PREROUTING链：用于目标地址转换(DNAT)；
- POSTOUTING链：用于源地址转换(SNAT)；
- 自定义的规则链；

**动作包括：**

ACCEPT/DROP/REJECT/LOG/RETURN/other_chain/等；

这里需要注意DROP和REJECT的区别，其中DROP是直接丢弃消息；而REJECT会给请求包一个错误提示。

另外，动作也可以是其他的自定义链。

**由于一般个人主机很少当做路由器使用，不会涉及到FORWARD链，因此，绝大部分的规则涉及到的表都是filter表，涉及到的链是INPUT和OUTPUT链。**

常用扩展
==========

可以使用如下命令查看支持的扩展：

::

    man iptables-extensions

    # 查看可用的内核模块
    ls /lib/modules/`uname -r`/kernel/net/netfilter/

    # 查看可用的iptables扩展
    # 在我的ubuntu-14.04系统上，提示没有该目录
    ls /usr/lib/iptables/

connlimit
+++++++++++

限制某个IP或者IP段对本机的并行连接数量。

选项解释(可以通过man iptables或者man iptables-extensions 查看每个选项具体含义)：

- ``--syn``: 表示该报文为syn报文，只针对TCP协议有效；
- ``--connlimit-above``: 已连接数量超过N时，则匹配；
- ``--reject-with``: 给匹配的包返回error packet响应；

limit
++++++

limi模块最初是用来限制日志记录速率，防止日志文件过大的。它也具有一定的限制包速率的功能。

::

    iptables -A INPUT -p tcp --dport 80 -m limit --limit 10/minute --limit-burst 100 -j ACCEPT

如我们可以使用上面的语句来防止网站DOS攻击。对于初始的100个HTTP请求，正常响应。而此后的HTTP请求，每分钟只会响应前10个。

- ``--limit`` 10/minute: 最大允许的连接速率限制。此例每分钟最多允许10个！
- ``--limit-burst``: 初始缓冲数量，只有总连接数量超过了该值，``--limit 10/minute`` 选项才会生效！

**实际上，根据ping测试结果，--limit 10/minute表示每6秒钟才会接受一次数据包。而并不是每分钟接接收前10个数据包！**

.. code-block:: console

    root@ubuntu:/smbshare/MyBlogs# iptables -S
    -P INPUT ACCEPT
    -P FORWARD ACCEPT
    -P OUTPUT ACCEPT
    -A INPUT -p icmp -m limit --limit 10/min --limit-burst 20 -j ACCEPT
    -A INPUT -p icmp -j DROP

另外需要注意：由于INPUT默认是ACCEPT策略，因此需要增加 ``-A INPUT -p icmp -j DROP`` 规则，否则对于不匹配的ICMP包，都会使用默认策略，
ping都可以收到回应！

.. figure:: /_static/images/ping_limit.png
   :scale: 100
   :align: center

   ping测试limit扩展, 每6个ping包只有一个收到回应


recent
+++++++

recent模块可以看作iptables里面维护了一个地址列表，这个地址列表可以通过:

- ``--set``: 将地址和时间戳添加进列表;
- ``--update``: 刷新时间戳;
- ``--rcheck``: 检查地址是否在列表;
- ``--remove``: 删除)四种方法来修改列表，每次使用时只能选用一种;

该模块还可附带:

- ``--name``: 参数来指定列表的名字(默认为DEFAULT)，
- ``--rsource/--rdest``: 指示当前方法应用到数据包的源地址还是目的地址(默认是前者)。

recent语句都带有布尔型返回值，每次(匹配)执行若结果为真，则会执行后续的语句(action)，比如 ``-j ACCEPT`` 之类的。

update和rcheck选项区别
-----------------------

在man手册页中，只是简单提到 ``--update`` 和 ``--rcheck`` 选项类似，除了更新时间戳之外。但是，
对两者的区别还是感到非常的疑惑，后来不断参阅资料、做实验，现在把自己理解的记录下来。

.. figure:: /_static/images/update_rcheck_diff.png
   :scale: 100
   :align: center

   update和rcheck选项区别测试

根据写的规则，先使用rcheck选项，进行ping测试；然后清空规则，然后使用update选项进行ping测试！

写的规则语义是：在10s钟内，最多允许有5个ICMP报文流进本机。

.. figure:: /_static/images/rcheck_ping.png
   :scale: 100
   :align: center

   rcheck选项ping测试

根据ping结果，很显然，rcheck选项首先允许5个ICMP包通过，然后后面的包丢弃；然后在下一个10s内，又允许5个ICMP包通过，一如此类。

.. figure:: /_static/images/update_ping1.png
   :scale: 100
   :align: center

   update选项ping测试

而在update选项中，只允许五个数据包通过，后面所有的ICMP包一律丢弃。

然后再来看另外一种测试方式，在这种方式中，我设置了ping的时间间隔，并在输出中显示时间戳。

.. figure:: /_static/images/update_ping2.png
   :scale: 100
   :align: center

   update选项ping测试2

根据大量的测试结果，可以看到update选项规则有如下特点：

- 假如10s内，收到的数据包少于5个，然后接下来的包可以正常接收；**或者换言之，假如收到连续5个包的时间大于10s，那么后续包可以正常处理**
- 假如收到连续5个包的时间少于10秒；那么在从最后收到的一个包时间戳开始计算，要等到下一个10s，才可以正常接收数据包，这10s期间的包，都直接丢弃。

string
+++++++

对数据包内容执行字符串匹配。

::

    # 该条规则表示，对于所有报文，如果报文内容有stack字符串，则丢弃报文。字符串匹配算法采用的是bm算法！
    iptables -R INPUT -p all -m string --algo bm --string "stack" -j DROP

iptables常用规则/命令
=====================

陆续收集和更新中……

限制每个ip的连接数量
++++++++++++++++++++

::

    # 通用语法
    iptables -A INPUT -p tcp --syn --dport $port -m connlimit --connlimit-above N -j REJECT --reject-with tcp-reset
    # 限制每个IP的ssh连接数量为三个！
    iptables -A INPUT -p tcp --syn --dport 22 -m connlimit --connlimit-above 3 -j REJECT

    # 限制http连接数量为20个！
    iptables -A INPUT -p tcp --syn --dport 80 -m connlimit --connlimit-above 20 -j REJECT --reject-with tcp-reset

    # 对上一条规则的优化，由于可能存在代理服务器，假设代理服务器ip为1.2.3.4，因此可用用 -d ! 忽略。
    iptables -A INPUT -p tcp --syn --dport 80 -d ! 1.2.3.4 -m connlimit --connlimit-above 20 -j REJECT --reject-with tcp-reset

    # 限制C类地址的HTTP连接数量为20个。
    iptables  -A INPUT -p tcp --syn --dport 80 -m connlimit --connlimit-above 20 --connlimit-mask 24 -j REJECT --reject-with tcp-reset


.. [#] https://www.cyberciti.biz/faq/iptables-connection-limits-howto/

解释：对某个特定IP，对本机某端口的TCP连接syn报文，如果已连接数量超过N，则丢弃syn连接报文，并返回tcp-reset报文！

限制每个ip的连接速率
+++++++++++++++++++++

以下这个脚本限制每个IP在100s的时间间隔内发起的http连接数量为10。

::

    #!/bin/bash
    IPT=/sbin/iptables
    # Max connection in seconds
    SECONDS=100
    # Max connections per IP
    BLOCKCOUNT=10
    # ....
    # ..
    # default action can be DROP or REJECT
    DACTION="DROP"
    $IPT -A INPUT -p tcp --dport 80 -i eth0 -m state --state NEW -m recent --set
    $IPT -A INPUT -p tcp --dport 80 -i eth0 -m state --state NEW -m recent --update --seconds ${SECONDS} --hitcount ${BLOCKCOUNT} -j ${DACTION}


其他
++++++++++

其他常用命令收集！

::

    # 设置INPUT/OUTPUT默认策略为丢弃
    iptables -P INPUT/OUTPUT DROP
    # 允许ssh远程登录
    iptables -A INPUT/OUTPUT -p tcp -m multiport --ports 22 -j ACCEPT

    # 允许samba共享, 首先查找samba相关服务端口
    netstat -platn | grep -P 'smb|samba'
    iptables -A INPUT/OUTPUT -p tcp -m multiport --ports 445,139 -j ACCEPT

    # 查看iptables规则
    iptables -S
    iptables -nvL --line-number
