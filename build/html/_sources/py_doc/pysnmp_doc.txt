[翻译] PySNMP教程
==================

.. contents:: 目录

--------------

.. note::

    地址：\ `PySNMP <http://pysnmp.sourceforge.net/contents.html>`__

    ``注``\ ：涉及到SNMP的专有名词一律不予以翻译, 并用粗体表示。

快速入门
--------

只要你在你的计算机上下载并安装了PySNMP库，你就可以解决非常基本的SNMP问题,
如通过Python命令行获取某个远程\ **SNMP
Agent**\ 的数据(你至少需要4.3.0以上版本，才可以执行后面的示例代码)。

获取SNMP变量
~~~~~~~~~~~~

复制和粘贴下列代码到Python命令提示符上，代码将会执行\ **SNMP
GET**\ 操作获取\ ``sysDescr.0``\ 对象，这是一个公开可用的\ **SNMP
Command Responder**,
更多对象请参考\ `demo.snmplabs.com <http://snmpsim.sourceforge.net/public-snmp-simulator.html>`__

.. code:: python

    """
    SNMPv1
    ++++++

    Send SNMP GET request using the following options:

      * with SNMPv1, community 'public'
      * over IPv4/UDP
      * to an Agent at demo.snmplabs.com:161
      * for two instances of SNMPv2-MIB::sysDescr.0 MIB object,

    Functionally similar to:

    | $ snmpget -v1 -c public demo.snmplabs.com SNMPv2-MIB::sysDescr.0

    """#
    from pysnmp.hlapi import *

    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget(('demo.snmplabs.com', 161)),
               ContextData(),
               ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
    )

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))

如果一切执行正常，那么将会在你的终端打印：

.. code:: python

    ...
    SNMPv2-MIB::sysDescr."0" = SunOS zeus.snmplabs.com 4.1.3_U1 1 sun4m
    >>>

发送\ **SNMP TRAP**
~~~~~~~~~~~~~~~~~~~

想给\ `demo.snmplabs.com <http://snmpsim.sourceforge.net/public-snmp-simulator.html>`__\ 中列出的宿主\ **Notification
Receiver**\ 发送\ **TRAP**\ 消息，复制以下代码到你的交互式Python会话中。

.. code:: python

    """
    SNMPv1 TRAP with defaults
    +++++++++++++++++++++++++

    Send SNMPv1 TRAP through unified SNMPv3 message processing framework
    using the following options:

    * SNMPv1
    * with community name 'public'
    * over IPv4/UDP
    * send TRAP notification
    * with Generic Trap #1 (warmStart) and Specific Trap 0
    * with default Uptime
    * with default Agent Address
    * with Enterprise OID 1.3.6.1.4.1.20408.4.1.1.2
    * include managed object information '1.3.6.1.2.1.1.1.0' = 'my system'

    Functionally similar to:

    | $ snmptrap -v1 -c public demo.snmplabs.com 1.3.6.1.4.1.20408.4.1.1.2 0.0.0.0 1 0 0 1.3.6.1.2.1.1.1.0 s "my system"

    """#
    from pysnmp.hlapi import *

    errorIndication, errorStatus, errorIndex, varBinds = next(
        sendNotification(
            SnmpEngine(),
            CommunityData('public', mpModel=0),
            UdpTransportTarget(('demo.snmplabs.com', 162)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity('1.3.6.1.6.3.1.1.5.2')
            ).addVarBinds(
                ('1.3.6.1.6.3.1.1.4.3.0', '1.3.6.1.4.1.20408.4.1.1.2'),
                ('1.3.6.1.2.1.1.1.0', OctetString('my system'))
            )
        )
    )

    if errorIndication:
        print(errorIndication)

许多\ **ASN.1
MIB**\ 文件可以通过\ `mibs.snmplabs.com <http://mibs.snmplabs.com/asn1/>`__\ 进行下载，也可以配置PySNMP自动下载他们。

参考手册
--------

SNMP历史
~~~~~~~~

在联网早期，计算机网络被当做是一项研究艺术而不是可被每个人使用的关键基础设施，网络管理更不被所知。当谁遇到了网络问题，他可能允许ping命令来定位问题源头，然后更改系统设置、重启软硬件，或叫同事在机房检查终端。

上世纪80年代，\ ``crash``
是一个很有意思的讨论，在网络管理工具之前，从\ `RFC
789 <https://tools.ietf.org/html/rfc789.html>`__\ 中也可以看到为了恢复和理解死机所付出的努力。工程师们事后研究等令人吃惊的事情可以从字里行间看到。由于互联网和内网从很小的网络长大成全球性的基础设施，网络也变得越来越重要，需要更系统的管理大量的软硬件设备。

因此当网络管理需求变得很清晰时，一个大学网络研究小组很快就开发并部署了SNMP。

**SNMP**\ 版本时间表：

    -  研究项目，SGMP
    -  SNMPv1,1988年，初始版本
    -  SNMPv2,1993年，完善
    -  SNMPv3,1999年，完全重新设计，保持先后兼容，并完全符合因特网标准

SNMP最初被认为是一个临时的解决方案，因为当时ISO正在开发一个听起来更具理论性的系统。由于对这个新网络管理系统的期待，SNMP开发者使得它很模块化。即使这种过渡从没有发生，SNMP的模块化特性使得它发展了三个主要版本，并并广泛使用和接受。

IETF
`RFC3411 <https://tools.ietf.org/html/rfc3411.html>`__\ 定义了SNMPv3，而\ `RFC3418 <https://tools.ietf.org/html/rfc3418.html>`__\ 定义了SNMP的当前标准。IETF已经制定SNMPv3具备完全的因特网标准(RFC的最成熟等级)。实际上，SNMP实现通常支持多个版本，典型的包括：SNMPv1，SNMPv2，SNMPv3。

*SNMP是否还有用？*
^^^^^^^^^^^^^^^^^^

联想到SNMP已经这么古老，你可能会有疑问为什么他还在使用，是否具有更现代的代替方案。很显然，SNMP仍是性能和故障管理的主要方式。SNMP被所有的网络设备和网络管理应用广泛支持。

SNMP如此顽强的一个主要原因是：由于SNMP的广泛部署，用其他系统代替需要巨大的努力；另外一个原因是因为当前在性能和错误管理上SNMP没有什么显著的缺陷。

另外，SNMP是免费的，没有被特定厂商控制，不要版权和许可费用，因此任何人都可以使用它，或者在它之上构建自己的SNMP产品。

尽管技术公司和标准制定机构付出很大努力，但是并没有什么新的网络监控标准产生。当前最杰出的代替品可能是\ `NETCONF <https://tools.ietf.org/html/rfc6241.html>`__\ ，然而他的重要目标是配置管理任务而不是错误和性能监控。此外，相对于SNMP，NETCONF更是资源密集型。

显然对每个人来说，提出自己的专用管理系统也是可能的。例如，在HTTPS/json之上这很容易做。但是，这只会对你的应用起作用，并且SSL引擎也会消耗更多的资源。

*当前和今后的用途*
^^^^^^^^^^^^^^^^^^

由于SNMP的广泛部署，在当前现代互联网上有多少支持SNMP的设备在运行时不可能的。因此人们可能只有要求SNMP监视整个互联网。

你可能发现SNMP对你的网络监控和管理很有用。例如你可以很容易的安装一个开源网络监控应用来监察、收集和绘图表示你家庭网络的WIFI路由器的带宽使用量(这可以帮你发现瓶颈)。

在未来几年，一个重大的变革可能会发生。这就是物联网。所有这些小功率设备都需要被监控和管理，这可能给SNMP技术带来新的生机。差不多三十年前，SNMP是为严重资源受限计算机而设计的。之后计算机变得越来越强大，资源也更多。现在我们重新回到构建大量的低功率设备为物联网，而原始SNMP的轻量级特性可以再一次为我们服务。

SNMP设计
~~~~~~~~

与他的名字所暗示的意思相反，SNMP可不仅仅是一个传输管理数据的协议。随着时间推移，它变得远比它最初设计者计划设计的复杂。

*术语标准和实体*
^^^^^^^^^^^^^^^^

在网络管理领域，各种组件和网络架构都有着它的特定专有术语，所以我们在这里引用这些术语。在这些术语中，最奇怪的是词汇"管理"(management)一词的过度使用，它几乎无处不在。

一个网络管理架构主要有三个组件：管理实体、被管理实体，和网络管理协议。

.. figure:: http://pysnmp.sourceforge.net/_images/nms-components.svg
   :alt: 此处输入图片的描述

   此处输入图片的描述

-  管理实体是一个运行在集中式网络管理工作站的应用程序。它就是一个控制、处理、分析、显示网络管理信息的实体。正是在这里，动作开始控制网络行为；也正是在这里，网络管理人员和网络设备进行交互。
-  被管理实体通常是驻留在被管理网络上硬件或软件应用，它枚举和形式化它的一些属性和状态，健康运行的重要，从而使它们提供给管理实体。例如，一个管理实体可以是一台主机，路由器，交换机，打印机，或任何其他设备。
-  网络管理系统的第三部分是网络管理协议。协议同时运行在管理和被管理实体上，运行管理实体查询被管理实体的状态，并通过代理执行随后的动作。

*结构和组件*
^^^^^^^^^^^^

SNMP由四个部分组成：

-  被称为MIB对象的网络管理对象的定义。管理信息通常被描述为被管理对象的集合，他们聚合一起形成虚拟的信息存储库，通常被称为管理信息库(Management
   Information Base,
   MIB)。一个MIB对象可能是一个计数器，一个描述信息(比如软件版本号)；状态信息(比如设备是否健康)或者是协议特定信息(比如到某个目的地的路由)。MIB对象因此定义了被管理节点所维护的管理信息。相关的MIB对象被收集起来放进一个所谓的MIB模块。
-  数据定义语言，称为SMI(Structure of Management
   Information，管理信息结构)，它提出了基本数据类型，并允许创建他们的子类型和更复杂的数据结构。MIB对象由这数据定义语言表示。
-  在管理对象和被管理对象之间传输信息的协议(SNMP)。SNMP的设计围绕C/S模型，有趣的是，管理实体和被管理实体都包含客户端和服务端组件。
-  可扩展的安全框架和系统管理能力。

后面的特征在SNMPv3之前的版本中完全不存在。

*数据类型*
^^^^^^^^^^

SMI提出了11种基础数据类型，用来描述被管理实体对象状态，他们要么是纯\ ``ASN.1``\ 类型，要么是他们的特例。

-  纯\ ``ASN.1``\ 类型：

   -  整形
   -  八位字节串
   -  对象标识符

``ASN.1``\ 是一个很古老和一系列很复杂的标准，用可迁移的方式(in a
portable way)来处理数据结构化和序列化的问题。

-  基本\ ``ASN.1``\ 类型的SNMP特定子类型有：

   -  Integer32/Unsigned32 - 32-bit integer
   -  Counter32/Counter64 - ever increasing number
   -  Gauge32 - positive, non-wrapping 31-bit integer
   -  TimeTicks - time since some event
   -  IPaddress - IPv4 address
   -  Opaque - uninterpreted ASN.1 string

对于标量类型(scalar
types)，SNMP定义了一种方式：把他们收集在一个有序数组中。从这些数组可以建立一个二维表。

PySNMP依赖于\ `PyASN1 <http://pyasn1.sf.net/>`__\ 包来塑模所有的SNMP类型，通过PyASN1，\ ``ASN.1``\ 类型实例可以表述为看起来像一个字符串或者整数的python对象。

我们可以相互转换PyASN1对象和Python类型，PyASN1对象可以进行基本的算术运算(数字)或字符串操作(串接等)。所有的SNMP基本类型和相对应的Python对象一样，都是不可变的。

.. code:: python

    >>> from pyasn1.type.univ import *
    >>> 
    >>> Integer(21) * 2
    Integer(42)
    >>> Integer(-1) + Integer(1)
    Integer(0)
    >>> int(Integer(42))
    42
    >>> OctetString('Hello') + ', ' + OctetString(hexValue='5079534e4d5021')
    OctetString('Hello, PySNMP!')
    >>> 

通过PySNMP传输和接收数据时，PySNMP库用户可能会遇到PyASN1类和对象。

我们会深入讨论的一个数据类型是\ ``OBJECT IDENTIFIER``\ ，它被用来命名一个对象。在该系统中，对象用层次式方式标识。

*对象标识符(OID)*
'''''''''''''''''

在计算对象标识符时广泛使用OID，它可以由三部分描述，每一个节点都被赋予不同的组织、域、概念或对象类型、具体对象实例。从人的角度来说，OID是一串数字，被点号隔开，用来编码节点。
|OID picture|
如图，该树的每一个分支都有一个数字和名称，而从树根到某个点的完整路径形成该点的名字，这个完整路径就是OID，靠近树根的节点通常具有极其普通的性质。

顶级MIB对象ID属于不同的标准化组织，厂商定义了私有分支包括自家产品的被管理对象。

是层次结构顶端是ISO和ITU-T，主要是这两个标准化组织做了ASN.1相关的工作，也是他们联合努力的一个分支。

在PyASN1模块中，OID像不可变数字序列，就像Python元组一样，PyASN1
OID对象可以被串接和切割，Subscription
操作(?这里不懂怎么翻译)返回一个数字的sub-OID。

.. code:: python

    >>> from pyasn1.type.univ import *
    >>> internetId = ObjectIdentifier((1, 3, 6, 1))
    >>> internetId
    ObjectIdentifier('1.3.6.1')
    >>> internetId[2]
    6
    >>> [ x for x in internetId ]
    [1, 3, 6, 1]
    >>> internetId + (2,)
    ObjectIdentifier('1.3.6.1.2')
    >>> internetId[1:3]
    ObjectIdentifier('3.6')
    >>> internetId[1]
    >>> = 2
    ...
    TypeError: object does not support item assignment

*对象集合*
^^^^^^^^^^

MIB可以理解为一系列相关被管理对象的形式化描述，这些被管理对象的整体值反应了子系统中被管理实体的当前状态。这些值可以通过给代理(代理运行在被管理节点上)发送SNMP消息被管理实体查询，修改或者上传。

例如，在打印机上，典型的监控对象通常是不同打印机墨盒状态、和已经打印的文件数量；在交换机上，关注的对象可能是流入流出流量、丢包率、广播处理的数据包数。

每一个被管理设备维持一个数据库，它的值是MIB中定义的每一项条目。\ **所以，可用数据并不取决于数据库，而是取决于实现。认识到这一点很重要：MIB文件不包含数据，他们在功能上和数据库模式(database
schemas)而不是数据存储相似。**

为了合适的组织MIB模块和对象，所有产品(来自于每个厂商)的可管理特性排列在MIB树结构中。每一个MIB模块和对象都有一个OID唯一标识。

SNMP管理实体和被管理实体都可以消费MIB信息。

-  管理实体

   -  通过MIB对象名查询OID
   -  转换值为合适的MIB对象类型
   -  阅读其他人留下的注释

-  被管理实体

   -  在代码中实现MIB对象

从人的视角来看，MIB是一个文本文件，使用ASN.1语言的子集编写。我们维护了一个超过9000个模块的MIB集合，你可以在你的项目中使用它。

PySNMP转换ASN.1
MIB文件为Python模块，然后SNMP引擎在运行时按需加载模块。PySNMP
MIB模块是通用的：同一个模块可以同时被管理实体和被管理实体使用。

MIB转换会由PySNMP自动执行，但是技术上，他是有PySNMP的姊妹工程PySMI处理的。当然，你也可以使用PySMI的mibdump.py工具手动完成这种转换。

*协议操作*
^^^^^^^^^^

SNMP围绕C/S模型设计，管理和被管理实体都包含客户端和服务端组件。客户端和服务端通过名字-值形式交换数据，值是强类型化的。

协议实体中间是SNMP殷勤，它用来协调所有的SNMP组件工作。 |snmp-engine.svg|
协议操作定义了两种形式：

-  Request-response消息
-  Unsolicited messages(主动提供的消息)

协议包含SNMP消息。除头部信息使用协议操作外，管理信息通过所谓的协议数据单元进行传输(Protocol
Data Units,
PDU)。SNMP定义了其中PDU类型，可以由管理实体和被管理实体(分别是管理者和代理)执行概念上不同的操作。

-  Manager-to-agent

   -  GetRequest, SetRequest, GetNextRequest, GetBulkRequest,
      InformRequest

-  Manager-to-manager

   -  InformRequest, Response

-  Agent-to-manager

   -  SNMPv2-Trap, Response

*核心应用*
^^^^^^^^^^

`RFC
3414 <https://tools.ietf.org/html/rfc3413.html>`__\ 标准标识了一系列标准SNMP应用，他们和管理实体或者被管理实体相关联。
|snmp-apps.svg|
PySNMP依据RFC和抽象服务接口实现了所有这些应用(通过原生SNMP
API)。这种方法的背后(backside)，是对大多数SNMP任务来说，它的做法很详细、啰嗦。为了使得SNMP易用，PySNMP提出了高级SNMP
API.

PySNMP架构
~~~~~~~~~~

我们可以从SNMP协议的进化来看PySNMP的内部结构。SNMP发展了很多年，从一个相对简单的协议到提起和结构化数据，再到一个可扩展的、模块化的、强加密和支持开箱即用的框架。

In the order from most ancient SNMP services to the most current ones,
what follows are different layers of PySNMP APIs:
从最古老的SNMP服务到最新版本，下面列出了不同层次的PySNMP API：

-  最底层和最基本的SNMPv1/v2c。它们支持程序员构建解析SNMP消息，处理协议级别错误，传输错误等。虽然被认为处理起来很复杂，这些API通常有最好的性能，内存弹性，除非需要支持MIB访问和SNMPv3.
-  SNMPv3标准在SNMP引擎和它的组件中配备了抽象服务接口。PySNMP实现采纳了这些抽象API并进行了扩展，所有他可以直接使用。额外的好处是，在这个层级进行PySNMP编程时API语义可以参考SNMP
   RFC。用户可以使用这些API实现自己的SNMP应用。
-  SNMPv3 `(RFC
   3413) <https://tools.ietf.org/html/rfc3413.html>`__\ 引入了核心SNMP应用的概念。PySNMP都实现了他们(在pysnmp.entity.rfc3413)，所以用户可以在这些核心SNMP应用之上构建自己的应用。
-  最后，为了SNMP对高频率任务易于使用，PySNMP配有一个高层次的核心SNMP应用和SNMP引擎服务(PySNMP
   comes with a high-level API to core SNMP applications and some of
   SNMP engine services.)。这下API在pysnmp.hlapi目录下，可以随时被使用。

此外还可以从代码角度看PySNMP内部：它包括少量大的、自包含并且良好定义的接口。下面的图片解释了PySNMP的功能结构：
|pysnmp-design.svg| PySNMP内部组件：

-  SNMP引擎是核心，是保护伞，它控制SNMP系统其它组件。典型的用户应用包含一个SNMP引擎类实例，该引擎类被各种SNMP应用共享。其它的组件用来构建不同的配置，运行时内部信息处理，SNMP引擎对象配置为可用状态很耗时。
-  传输子系统用来传输或接收SNMP消息。I/O子系统由一个抽象的分发器(Dispatcher)和一个(或多个)抽象Transport类。具体Dispatcher事项是特定的I/O方法，比如BSD套接字。具体的Transport类是特定的传输域。SNMP通常使用UDP传输(但是其他的传输协议也是可能的)。Transport
   Dispatcher接口通常被Message And PDU
   Dispatcher使用。不过，如果使用SNMPv1/v2c原生API(最底层的API)，这些接口会被直接调用。
-  Message and PDU
   Dispatcher是SNMP消息处理活动的地方，它的主要任务包括：把SNMP应用从不同子系统收集的PDU向下传输给Transport
   Dispatcher，并把来自于网络的SNMP消息向上传输到SNMP应用(Its main
   responsibilities include dispatching PDUs from SNMP Applications
   through various subsystems all the way down to Transport Dispatcher,
   and passing SNMP messages coming from network up to SNMP
   Applications)。它维持和管理控制器间的逻辑连接，管理控制器在被管理对象上执行操作。这是为了LCD访问。
-  消息处理模块为当前和未来可能版本的SNMP协议处理消息层级的协议操作。最重要的是，这些模块包括消息解析、构建和安全调用服务(当需求的时候)。
-  消息安全模块处理消息认证和加密。在编写这一文档时，基于用户的(主要是v3)和社区(主要是v1/2c)的模块在PySNMP中已经实现。所有这些安全模块共享相同的API(这些API被消息处理子系统使用)。
-  访问控制系统使用LCD(Local Configuration
   Datastore)来认证对被管理对象的远程访问。当使用代理身份运行时，它就会被使用。
-  一系列MIB模块和对象集合，被SNMP引擎用来维持配置和数据操作统计。他们整体被称作LCD。

在大部分情况下，用户都只期望使用高层API。可是，实现SNMP
Agent，Proxy和manager的一些不常见特性时，都需要使用标准应用API。这时，理解SNMP操作和SNMP引擎组件是有益处的。

常用操作
~~~~~~~~

在这份教程中，我们会循序渐进，运行一系列SNMP请求命令和通知。我们会用高级PySNMP同步API，这使用起来最简单。

*创建SNMP引擎*
^^^^^^^^^^^^^^

SNMP引擎是核心，保护伞。所有的PySNMP操作都涉及到\ ``SnmpEngine``\ 对象实例。PySNMP
APP可以运行多个独立SNMP引擎，每个都被它自己的SnmpEngine对象操纵。

.. code:: python

    >>> from pysnmp.hlapi import *
    >>> 
    >>> SnmpEngine()
    SnmpEngine(snmpEngineID=SnmpEngineID())

SNMP引擎有一个独立的标识符，它可以被自动赋值，也可以管理方式赋值。这个标识符在SNMP协议操作中会被使用。

*执行SNMP查询*
^^^^^^^^^^^^^^

我们将会发送SNMP
GET命令从SNMP代理中读取MIB对象。为此我们将会调用同步高级API
getCmd()函数。也可以使用类似的方式调用相应的函数来执行SNMP命令。

.. code:: python

    >>> from pysnmp.hlapi import *
    >>> [ x for x in dir() if 'Cmd' in x]
    ['bulkCmd', 'getCmd', 'nextCmd', 'setCmd']
    >>> getCmd
    <function getCmd at 0x222b330>

*选择SNMP协议和证书*
^^^^^^^^^^^^^^^^^^^^

我们有三个SNMP协议版本可供选择。想使用SNMPv1/v2c，我们可以传递合适的\ ``CommunityData``\ 类初始化实例；想使用v3可以传递\ ``UsmUserData``\ 类实例。

SNMP社区名字，在你选择v1/v2c时，就通过\ ``CommunityData``\ 对象传给SNMP
LCD。

.. code:: python

    >>> CommunityData('public', mpModel=0)  # SNMPv1
    CommunityData(communityIndex='s-855862937891009719', communityName=<COMMUNITY>, mpModel=0, contextEngineId=None, contextName='', tag='', securityName='s-855862937891009719')
    >>> CommunityData('public', mpModel=1)  # SNMPv2c
    CommunityData(communityIndex='s-2208453704422760742', communityName=<COMMUNITY>, mpModel=1, contextEngineId=None, contextName='', tag='', securityName='s-2208453704422760742')

使用\ ``UsmUserData``\ 对象进行LCD配置暗示使用SNMPv3。除了需要设置USM用户名字，UsmUserData对象也可以携带加密秘钥和加密协议协议给SNMP引擎LCD。

.. code:: python

    >>> UsmUserData('testuser', authKey='myauthkey')
    UsmUserData(userName='testuser', authKey=<AUTHKEY>, privKey=<PRIVKEY>, authProtocol=(1, 3, 6, 1, 6, 3, 10, 1, 1, 2), privProtocol=(1, 3, 6, 1, 6, 3, 10, 1, 2, 1), securityEngineId='<DEFAULT>', securityName='testuser')
    >>> UsmUserData('testuser', authKey='myauthkey', privKey='myenckey')
    UsmUserData(userName='testuser', authKey=<AUTHKEY>, privKey=<PRIVKEY>, authProtocol=(1, 3, 6, 1, 6, 3, 10, 1, 1, 2), privProtocol=(1, 3, 6, 1, 6, 3, 10, 1, 2, 2), securityEngineId='<DEFAULT>', securityName='testuser')

PySNMP支持md5和sha消息认证算法，des，aes128/192/356和3des加密算法。

为了简便，我们将使用SNMPv2。虽然不完全安全，但它仍然是使用最广泛的SNMP版本。

*设置传输和目标*
^^^^^^^^^^^^^^^^

PySNMP支持UDP-over-IPv4和UDP-over-IPv6网络传输。
在这个例子里，我们将会查询demo.snmplabs.com网站上可通过IPv4访问的public
SNMP
simulator。传输配置以相应的合适的\ ``UdpTransportTarget``\ 和\ ``Udp6TransportTarget``\ 对象传递给SNMP
LCD。

*处理SNMP上下文*
^^^^^^^^^^^^^^^^

SNMP上下文是SNMPv3消息头的一个参数，它用来处理特定的MIB集合(这些MIB让被管理实体的SNMP引擎使用)。SNMP引擎可以服务很多同一的MIB对象(这些对象代表完全不同的被管理的软硬件实体)。这就是需要snmp上下文的原因。

可以使用一个合适的初始\ ``ContextData``\ 对象来表明snmp上下文位于高层API。在这个例子里，我们使用的是\ ``empty``\ 上下文(默认)。

.. code:: python

    >>> g = getCmd(SnmpEngine(),
    ...            CommunityData('public'),
    ...            UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...            ContextData(),

*指定MIB对象*
^^^^^^^^^^^^^

最后，我们需要指定我们想要读取的MIB对象。在协议层，MIB对象由OID标识，但是人们想要用名字处理他们：

.. code:: powershell

    $ snmpget -v2c -c public demo.snmplabs.com SNMPv2-MIB::sysDescr.0
    SNMPv2-MIB::sysDescr.0 = STRING: SunOS zeus.snmplabs.com
    $
    $ snmpget -v2c -c public demo.snmplabs.com 1.3.6.1.2.1.1.1.0
    SNMPv2-MIB::sysDescr.0 = STRING: SunOS zeus.snmplabs.com

对象名字和OID都来自于MIB。名字和OID的关联由称作\ ``OBJECT-TYPE``\ 的高级SMI结构完成。这里有MIB对象定义的例子：sysUpTime，它的OID是...mgmt.mib-2.system.3，它的值类型是\ ``TimeTicks``\ 。

::

    sysUpTime OBJECT-TYPE
        SYNTAX      TimeTicks
        MAX-ACCESS  read-only
        STATUS      current
        DESCRIPTION
                "The time (in hundredths of a second) since
                the network management portion of the system
                was last re-initialized."
        ::= { system 3 }

在PySnmp中，我们使用\ ``ObjectIdentity``\ 类来负责MIB对象标识。ObjectIdentity代表从人的视角来处理MIB对象的方式。它需要转换MIB到一个完全可解析的状态。ObjectIdentity可以由MIB对象名字初始化，之后它的行为就类似OID了。

.. code:: python

    >>> from pysnmp.hlapi import *
    >>>
    >>> x = ObjectIdentity('SNMPv2-MIB', 'system')
    >>> # ... calling MIB lookup ...
    >>> tuple(x)
    (1, 3, 6, 1, 2, 1, 1, 1)
    >>> x = ObjectIdentity('iso.org.dod.internet.mgmt.mib-2.system.sysDescr')
    >>> # ... calling MIB lookup ...
    >>> str(x)
    '1.3.6.1.2.1.1.1'

MIB解析意思是MIB对象名到OID转型服务，反过来亦然。

PySNMP中，\ ``ObjectType``\ 类实例代表\ ``OBJECT-TYPE``
SMI结构。ObjectType是一个容器对象，它引用ObjectIdentity和SNMP类型实例。作为一个Python对象，它更像是一个(OID,
value)元组。

.. code:: python

    >>> from pysnmp.hlapi import *
    >>> x = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0), 'Linux i386 box'))
    >>> # ... calling MIB lookup ...
    >>> x[0].prettyPrint()
    'SNMPv2-MIB::sysDescr.0'
    >>> x[1].prettyPrint()
    'Linux i386 box'

尾随表示MIB对象实例。MIB中描述的对象仅仅是声明，它从来不包含任何数据。Data
is stored in MIB object instances that are addressed by appending For
scalar MIB objects index is ‘0’ by
convention(这句不知该任何翻译)。\ ``ObjectIdentity``\ 类使用索引进行初始化。

.. code:: python

    >>> x = ObjectIdentity('SNMPv2-MIB', 'system', 0)
    >>> # ... calling MIB lookup ...
    >>> tuple(x)
    (1, 3, 6, 1, 2, 1, 1, 1, 0)

我们将读取sysDescr标量MIB对象实例，他在\ `SNMPv2-MIB <http://mibs.snmplabs.com/asn1/SNMPv2-MIB>`__\ 模块中定义。

.. code:: python

    >>> from pysnmp.hlapi import *
    >>> g = getCmd(SnmpEngine(),
    ...            CommunityData('public'),
    ...            UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...            ContextData(),
    ...            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))

默认的，PySNMP将会在你的文件系统中搜索你参考的ASN.1
MIB文件。也可以配置成从远程主机自动下载他们，\ `比如这个例子 <http://pysnmp.sourceforge.net/examples/hlapi/asyncore/sync/manager/cmdgen/mib-tweaks.html>`__\ 。我们维护了一系列ASN.1模块集合，你可以在你的项目中使用他们。

*读取标量值*
^^^^^^^^^^^^

我们终于可以发送SNMP查询，并期待接收一些有意义的应答了。

同步API的一个显著特征是它围绕Python生成器构造的。每次函数调用结束后，都会返回一个生成器对象。迭代生成器对象就会执行真实的SNMP通信。在每一次迭代中构建并发送SNMP消息，等待应答，接收并解析。

.. code:: python

    >>> from pysnmp.hlapi import *
    >>>
    >>> g = getCmd(SnmpEngine(),
    ...            CommunityData('public'),
    ...            UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...            ContextData(),
    ...            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)))
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0'), TimeTicks(44430646))])

*SNMP表*
^^^^^^^^

    译注：SNMP
    tables是一个术语概念，实际上前面提到都是SNMP简单对象，SNMP还可以操作复合对象。它可以类比于C语言中的结构体。更多细节，请参考Stevens的《TCP/IP详解》

SNMP定义了表的概念。表用于当一个MIB对象拥有多个属性实例时。例如：网络接口属性放在了SNMP表中。每一个属性实例由MIB对象+后缀进行处理。

MIB详细描述了表，他们的索引由\ ``INDEX``\ 子句声明。表索引可能是非0整数，字符串，或SNMP基础类型。

在协议层，所有的索引以OID形式呈现。为了方便人们使用索引，SNMP管理应用依赖\ ``DISPLAY-HINT``\ 子句在OID和SNMP特定类型间自动转换索引，更友好的呈现给用户。

::

    ifEntry OBJECT-TYPE
        SYNTAX      IfEntry
        INDEX   { ifIndex }
    ::= { ifTable 1 }

    ifIndex OBJECT-TYPE
        SYNTAX      InterfaceIndex
    ::= { ifEntry 1 }

    ifDescr OBJECT-TYPE
        SYNTAX      DisplayString (SIZE (0..255))
    ::= { ifEntry 2 }

    InterfaceIndex ::= TEXTUAL-CONVENTION
        DISPLAY-HINT "d"
        SYNTAX       Integer32 (1..2147483647)

在PySNMP中用法是：

::

    >>> x = ObjectIdentity('IF-MIB', 'ifDescr', 123)
    >>> # ... calling MIB lookup ...
    >>> str(x)
    '1.3.6.1.2.1.2.2.1.2.123'

有些SNMP表可以由很多索引进行检索，每一个索引都会成为OID的一部分，并最终包含在MIB对象OID里。

从语义上来看，每个索引代表MIB对象的一个重要和不同的属性。

::

    tcpConnectionEntry OBJECT-TYPE
        SYNTAX  TcpConnectionEntry
        INDEX   { tcpConnectionLocalAddressType,
                  tcpConnectionLocalAddress,
                  tcpConnectionLocalPort,
                  tcpConnectionRemAddressType,
                  tcpConnectionRemAddress,
                  tcpConnectionRemPort }
    ::= { tcpConnectionTable 1 }

    tcpConnectionLocalPort OBJECT-TYPE
        SYNTAX     InetPortNumber
    ::= { tcpConnectionEntry 3 }

在PySNMP中，\ ``ObjectIdentity``\ 类可以携带任意个索引参数，这些索引参数以对用户方式呈现，并转化为完整的OID：

::

    >>> x = ObjectIdentity('TCP-MIB', 'tcpConnectionState',
    ...                    'ipv4', '195.218.254.105', 41511,
    ...                    'ipv4', '194.67.1.250', 993)
    >>> # ... calling MIB lookup ...
    >>> str(x)
    '1.3.6.1.2.1.6.19.1.7.1.4.195.218.254.105.41511.1.4.194.67.1.250.993'

让我们为一个TCP连接读取\ ``TCP-MIB::tcpConnectionState``\ 对象。

::

    >>> from pysnmp.hlapi import *
    >>>
    >>> g = getCmd(SnmpEngine(),
    ...            CommunityData('public'),
    ...            UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...            ContextData(),
    ...            ObjectType(ObjectIdentity('TCP-MIB', 'tcpConnectionState',
    ...                                      'ipv4', '195.218.254.105', 41511,
    ...                                      'ipv4', '194.67.1.250', 993)
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.2.1.6.19.1.7.1.4.195.218.254.105.41511.1.4.194.67.1.250.993')), Integer(5))])

*SNMP命令操作*
^^^^^^^^^^^^^^

    译注：SNMP的next命令，可以获取MIB树的下一个属性，这样运行我们通过迭代的方式获取所有MIB属性。详情请参考《TCP/IP详解》

SNMP允许你获取一个给定MIB对象的下一个。这样你可以读取你事先并不知道的MIB对象。MIB对象是依据他们的OID进行字典排序的，\ ``nextCmd``\ 函数实现了这个特性。

    译注：对于SNMP简单MIB对象，是依据OID进行排序；对于SNMP表，是依据\ ``先列后行``\ 方式排列的。

::

    >>> from pysnmp.hlapi import *
    >>> g = nextCmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...             ContextData(),
    ...             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr')))
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'), DisplayString('SunOS zeus.snmplabs.com'))])
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.2.0'), ObjectIdentity(ObjectIdentifier('1.3.6.1.4.1.8072.3.2.10')))])

迭代生成器对象会遍历SNMP代理的MIB对象。

SNMPv2c对\ ``GETNEXT``\ 命令进行了重大优化——它的修订版本称作\ ``GETBULK``\ ，并能立刻对一系列next
MIB对象进行收集和响应。额外的非中继和最大可重复参数可以用来影响MIB对象分批处理(Additional
non-repeaters and max-repetitions parameters can be used to influence
MIB objects batching.)。

PySNMP在协议层隐藏了\ ``GETBULK``\ 优化，bulkCmd()函数暴露了同样的生成器API，使getNext()使用更方便。

.. code:: python

    >>> from pysnmp.hlapi import *
    >>>
    >>> N, R = 0, 25
    >>> g = bulkCmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...             ContextData(),
    ...             N, R,
    ...             ObjectType(ObjectIdentity('1.3.6')))
    >>>
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'), DisplayString('SunOS zeus.snmplabs.com'))])
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.2.0'), ObjectIdentifier('1.3.6.1.4.1.20408'))])

Python生成器不仅可以产生数据，也可以给运行中的生成器对象发送数据。这个特性被高级API用来为一系列MIB对象重复相同的SNMP操作。

.. code:: python

    >>> from pysnmp.hlapi import *
    >>>
    >>> g = nextCmd(SnmpEngine(),
    ...             CommunityData('public'),
    ...             UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...             ContextData(),
    ...             ObjectType(ObjectIdentity('IF-MIB', 'ifTable')))
    >>>
    >>> g.send([ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets'))])
    (None, 0, 0, [(ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.1'), Counter32(284817787))])

你可以通过把他们放在一个PDU中来操作很多不相干的MIB对象。应答PDU也会携带一系列MIB对象，他们的值和请求消息的排列顺序相同。

.. code:: Python

    >>> from pysnmp.hlapi import *
    >>>
    >>> g = getCmd(SnmpEngine(),
    ...            CommunityData('public'),
    ...            UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...            ContextData(),
    ...            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
    ...            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0))
    ... )
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'), DisplayString('SunOS zeus.snmplabs.com')), ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0'), TimeTicks(44430646))])

部分SNMP配置管理依赖于\ ``SNMP SET``\ 命令。虽然在被管理实体端，它的实现被证明很苛刻(由于锁和事务行为)。所以厂商趋向于移除它，致使被管理实体是只读的。

PySNMP通过\ ``setCmd()``\ 函数支持统一的set操作。

.. code:: Python

    >>> from pysnmp.hlapi import *
    >>>
    >>> g = setCmd(SnmpEngine(),
    ...            CommunityData('public'),
    ...            UdpTransportTarget(('demo.snmplabs.com', 161)),
    ...            ContextData(),
    ...            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0), 'Linux i386')
    ... )
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'), DisplayString('Linux i386'))])

*发送SNMP通知*
^^^^^^^^^^^^^^

被管理实体可以发送未经请求的消息给管理实体。这杯称为通知，通知可以减少轮训(轮询在大规模网络中可能会成为一个问题。)

SNMP通知是被枚举的(SNMP notifications are
enumerated)，并且每一个都有确切的语义。这是通过一个特殊的，高级的SMI结构\ ``NOTIFICATION-TYPE``\ 完成的。和\ ``OBJECT-TYPE``\ 定义一个MIB对象类似，\ ``NOTIFICATION-TYPE``\ 也有一个唯一的OID，但是它的SNMP值引用的是其他MIB对象序列。这些MIB对象在通知被发送时用\ ``OBJECTS``\ 子句指定，他们的当前值被包含在通知消息中。

.. code:: Python

    linkUp NOTIFICATION-TYPE
        OBJECTS { ifIndex, ifAdminStatus, ifOperStatus }
        STATUS  current
        DESCRIPTION
            "..."
    ::= { snmpTraps 4 }

为了在PySNMP中塑模\ ``NOTIFICATION-TYPE``\ 结构，我们用\ ``NotificationType``\ 类，这是一个包装对象。它被\ ``ObjectIdentity``\ 类标识，并引用一系列\ ``ObjectType``\ 类实例。

从行为角度看，\ ``NotificationType``\ 看起来像\ ``ObjectType``\ 类对象序列。

.. code:: Python

    >>> from pysnmp.hlapi import *
    >>>
    >>> x = NotificationType(ObjectIdentity('IF-MIB', 'linkUp'))
    >>> # ... calling MIB lookup ...
    >>> >>> [ str(y) for x in n ]
    ['SNMPv2-MIB::snmpTrapOID.0 = 1.3.6.1.6.3.1.1.5.3', 'IF-MIB::ifIndex = ', 'IF-MIB::ifAdminStatus = ', 'IF-MIB::ifOperStatus = ']

用PySNMP发送SNMP通知和发送SNMP命令并没有太大不同。不同点在于如何构建PDU
var-binds(The difference is in how PDU var-binds are
built)。在SNMP中存在两种不同的通知：\ ``trap``\ 和\ ``inform``\ 。

对于\ ``trap``\ ，agent-to-manager通信是单向的，不会发送响应和确认。

.. code:: Python

    >>> from pysnmp.hlapi import *
    >>>
    >>> g = sendNotification(SnmpEngine(),
    ...                      CommunityData('public'),
    ...                      UdpTransportTarget(('demo.snmplabs.com', 162)),
    ...                      ContextData(),
    ...                      'trap',
    ...                      NotificationType(ObjectIdentity('IF-MIB', 'linkUp'), instanceIndex=(123,))
    ... )
    >>> next(g)
    (None, 0, 0, [])

``inform``\ 更像是一个命令，不同点在于PDU格式。\ ``inform``\ 用于manager-to-manager通信，也用于agent-to-manager通信。

.. code:: Python

    >>> from pysnmp.hlapi import *
    >>>
    >>> g = sendNotification(SnmpEngine(),
    ...                      CommunityData('public'),
    ...                      UdpTransportTarget(('demo.snmplabs.com', 162)),
    ...                      ContextData(),
    ...                      'inform',
    ...                      NotificationType(ObjectIdentity('IF-MIB', 'linkUp'), instanceIndex=(123,))
    ... )
    >>> next(g)

在后面的例子你会看到从IF-MIB::linkUp通知中自动扩展的MIB对象(ifIndex,
ifAdminStatus,
ifOperStatus)。为了通过索引处理SNMP表对象特定的行，可以用\ ``instanceIndex``\ 参数给\ ``NotificationType``\ 传递MIB对象的索引部分。

如你所见，扩展MIB对象的实际值为null。这是因为在我们的例子脚本没有访问这些MIB对象。我们可以提供这些缺失的信息：给\ ``NotificationType``\ 传递一个字典对象(该字典对象是MIB对象OID和当前值的映射)。

.. code:: Python

    >>> from pysnmp.hlapi import *
    >>>
    >>> mib = {ObjectIdentifier('1.3.6.1.2.1.2.2.1.1.123'): 123,
    ...        ObjectIdentifier('1.3.6.1.2.1.2.2.1.7.123'): 'testing',
    ...        ObjectIdentifier('1.3.6.1.2.1.2.2.1.8.123'): 'up'}
    >>>
    >>> g = sendNotification(SnmpEngine(),
    ...                      CommunityData('public'),
    ...                      UdpTransportTarget(('demo.snmplabs.com', 162)),
    ...                      ContextData(),
    ...                      'inform',
    ...                      NotificationType(ObjectIdentity('IF-MIB', 'linkUp'), instanceIndex=(123,), objects=mib)
    ... )
    >>> next(g)
    (None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0'), TimeTicks(0)), ObjectType(ObjectIdentity('1.3.6.1.6.3.1.1.4.1.0'), ObjectIdentity('1.3.6.1.6.3.1.1.5.4')), ObjectType(ObjectName('1.3.6.1.2.1.2.2.1.1.123'), InterfaceIndex(123)), ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.7.123'), Integer(3)), ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.8.123'), Integer(1))])

*大容量消息*
^^^^^^^^^^^^

当提到管理大规模网络时，顺序读取MIB对其会有时延。在某些方面，这些时延是不可忍受的。一种广为人知的方法是并行化查询——你可以在用多线程、多进程方式执行这些操作，或者围绕异步I/O模型构建你的应用程序。

和其他方式相比，异步模型最轻量级、最具扩展性。它的思想很简单：\ **永远不要等待I/O——只要可能就去做其他的事情**\ 。这种方式的缺点是执行流不再是线性的，这将导致程序源码难以阅读分析。

PySNMP高级API采用三种异步I/O框架——asyncore，twisted和asyncio。异步API的更多信息，请参考PySNMP库参考手册和\ `相关示例 <http://pysnmp.sourceforge.net/examples/contents.html>`__

.. |OID picture| image:: http://pysnmp.sourceforge.net/_images/oid-tree.svg
.. |snmp-engine.svg| image:: http://pysnmp.sourceforge.net/_images/snmp-engine.svg
.. |snmp-apps.svg| image:: http://pysnmp.sourceforge.net/_images/snmp-apps.svg
.. |pysnmp-design.svg| image:: http://pysnmp.sourceforge.net/_images/pysnmp-design.svg
