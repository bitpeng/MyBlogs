.. _iptables_sum:


########################
iptables 学习总结
########################

**date: 2017-02-17 10:30**

.. contents:: 目录

--------------------------

近期调研neutron-metering-agent组件，需要事先熟悉下iptables，把自己学习iptables的相关知识点记录下来，以供参考。


.. figure:: /_static/images/kvm_error.png
   :scale: 100
   :align: center

   KVM启动虚拟机错误


命令格式
=========

iptables操作规则的命令格式如下：

::

    iptables [-t 表名] <-A/I/D/R> 规则链名 [规则号] \
             <-i/o 网卡名> -p 协议名 <-s 源IP/源子网> \
             --sport 源端口 <-d 目标IP/目标子网> --dport 目标端口 \
             [-m 扩展模块 匹配条件]
             -j 动作

其中， **表名包括：**

- raw：高级功能，如：网址过滤。
- mangle：数据包修改（QOS），用于实现服务质量。
- net：地址转换，用于网关路由器。
- filter：包过滤，用于防火墙规则。

*假如表名没有指定的话，则默认是filter*

**规则链包括：**

- INPUT链：处理输入数据包。
- OUTPUT链：处理输出数据包。
- PORWARD链：处理转发数据包。
- PREROUTING链：用于目标地址转换(DNAT)。
- POSTOUTING链：用于源地址转换(SNAT)。
- 自定义的规则链。


.. [#] http://man.linuxde.net/iptables

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
----------

限制某个IP或者IP段对本机的并行连接数量。

选项解释(可以通过man iptables或者man iptables-extensions 查看每个选项具体含义)：

- ``--syn``: 表示该报文为syn报文，只针对TCP协议有效；
- ``--connlimit-above``: 已连接数量超过N时，则匹配；
- ``--reject-with``: 给匹配的包返回error packet响应；



iptables常用实例收集
=====================

陆续收集和更新中……

限制每个ip的连接数量
-----------------------

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
-----------------------

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

.. [#] https://www.cyberciti.biz/faq/iptables-connection-limits-howto/
