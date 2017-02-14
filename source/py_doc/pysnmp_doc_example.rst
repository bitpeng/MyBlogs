PySNMP获取设备信息
==================

.. contents:: 目录

--------------





.. note::
    该文档，将以简单的例子，示范使用PySNMP库获取设备信息的思路和方法。有关snmp协议和PySNMP库的更多信息，可以参考之前的文档《PySNMP教程》。

--------------

首先, 可以获取的mib信息，都在网站\ `mibs.snmplabs.com <http://mibs.snmplabs.com/asn1/>`__\ 可以找到，比如，我们需要查询cpu的某些信息。

.. code-block:: console

    root@ubuntu:/smbshare# snmpwalk -v 2c -c public 10.11.113.150 ssCpuIdle
    UCD-SNMP-MIB::ssCpuIdle.0 = INTEGER: 93

然后打开UCD-SNMP-MIB目录，可以找到cpu相关的mib对象。

.. figure:: /_static/images/snmp_ucd.png
   :scale: 100
   :align: center

   ucd

.. figure:: /_static/images/snmp_sscpu.png
   :scale: 100
   :align: center

   sscpu

在description里有关于对象信息的详细解释。

cpu信息
-------

根据\ `UCD-SNMP-MIB文件 <http://mibs.snmplabs.com/asn1/UCD-SNMP-MIB>`__\ ，可以获取的cpu参数共有33条，这里我们主要关注的是cpu的使用率，\ ``ssCpuIdle``\ 获取的是cpu的空闲率，所以100
- ssCpuIdle 既可以求得cpu的使用率。

.. code:: Python

    def getCpuUsage(targetHost, targetPort, cmd, community):
        errIndication, errStatus, errIndex, varBindTable = cmd.nextCmd(
            cmdgen.CommunityData(community, mpModel=1),     # mpModel=1,表示使用v2协议
            cmdgen.UdpTransportTarget((targetHost,targetPort)), # 设备ip及端口
            cmdgen.MibVariable('UCD-SNMP-MIB','ssCpuIdle'),  # 需要访问信息的MIB库及子节点，也可以用形如'1.3.6.1.4'(OID标识符)的方式来定义
            #lookupValues=True
        )
        if errIndication:
            print errIndication
        else:
            if errStatus:
                print '%s at %s' % (
                    errStatus.prettyPrint(),
                    errIndex and varBindTable[-1][int(errIndex)-1] or '?'
                    )
            else:
                return 100.0 - float(varBindTable[0][0][1].prettyPrint())

这是运行结果：

::

    [[ObjectType(ObjectIdentity(ObjectName('1.3.6.1.4.1.2021.11.11.0')), Integer32(92))]]
    CPU使用率：8.0

内存信息
--------

可以获取的完整内存对象信息也在\ ``http://mibs.snmplabs.com/asn1/UCD-SNMP-MIB``\ 上，包括memTotalFree，memShared，memBuffer等。

.. code:: python

    def getMemUsage(targetHost, targetPort, cmd, community):
        errIndication, errStatus, errIndex, varBindTable = cmd.nextCmd(
            cmdgen.CommunityData(community, mpModel=1),
            cmdgen.UdpTransportTarget((targetHost,targetPort)),
            cmdgen.MibVariable('UCD-SNMP-MIB','memTotalReal'), #'1.3.6.1.4.1.2021.4.5',
            cmdgen.MibVariable('UCD-SNMP-MIB','memAvailReal'), #'1.3.6.1.4.1.2021.4.6',
            cmdgen.MibVariable('UCD-SNMP-MIB','memBuffer'), #'1.3.6.1.4.1.2021.4.14',
            cmdgen.MibVariable('UCD-SNMP-MIB','memCached'), # '1.3.6.1.4.1.2021.4.15',
            #cmdgen.MibVariable('UCD-SNMP-MIB', 'memTotalSwap'),
            #lookupValues=True
            #lookupNames=True
        )
        #print varBindTable
        if errIndication:
            print errIndication
        else:
            if errStatus:
                print '%s at %s' % (
                    errStatus.prettyPrint(),
                    errIndex and varBindTable[-1][int(errIndex)-1] or '?'
                    )
            else:
                mysum = 0.0
                totalAvailReal = float(varBindTable[0][0][1].prettyPrint())
                for var in varBindTable:
                    for name , val in var:
                        mysum += float(val.prettyPrint())
                return totalAvailReal, (2*totalAvailReal - mysum) / totalAvailReal * 100.0

其中，比较重要的内存信息有：内存总量，缓冲区大小，cache区大小，swap区大小等。据此，可以计算出内存的使用率。

disk信息
--------

disk的相关信息也定义在mib文件UCD-SNMP-MIB中，根据该文件，可以获取以下disk信息：

::

    DskEntry ::= SEQUENCE {
        dskIndex        Integer32,
        dskPath     DisplayString,
        dskDevice       DisplayString,
        dskMinimum      Integer32,
        dskMinPercent   Integer32,
        dskTotal        Integer32,
        dskAvail        Integer32,
        dskUsed     Integer32,
        dskPercent      Integer32,
        dskPercentNode  Integer32,
        dskErrorFlag    UCDErrorFlag,
        dskErrorMsg     DisplayString,
        dskTotalLow     Unsigned32,
        dskTotalHigh    Unsigned32,
        dskAvailLow     Unsigned32,
        dskAvailHigh    Unsigned32,
        dskUsedLow      Unsigned32,
        dskUsedHigh     Unsigned32
    }

根据oid
name，可以很容易看出其意思，下面的代码可以用来获取disk的使用信息：

.. code:: python

    def getDiskUsage(targetHost, targetPort, cmd, community):
        errIndication, errStatus, errIndex, varBindTable = cmd.nextCmd(
            cmdgen.CommunityData(community, mpModel=1),
            cmdgen.UdpTransportTarget((targetHost,targetPort)),
            cmdgen.MibVariable('UCD-SNMP-MIB', 'dskPath'), # '1.3.6.1.4.1.2021.9.1.2'
            cmdgen.MibVariable('UCD-SNMP-MIB', 'dskTotal'), # '1.3.6.1.4.1.2021.9.1.6'
            cmdgen.MibVariable('UCD-SNMP-MIB', 'dskPercent'), #'1.3.6.1.4.1.2021.9.1.9'
            cmdgen.MibVariable('UCD-SNMP-MIB', 'dskDevice'), #'1.3.6.1.4.1.2021.9.1.3'
            #lookupValues=True,
            #lookupNames=True
        )
        if errIndication:
            print errIndication

        else:
            if errStatus:
                print '%s at %s' % (errStatus.prettyPrint(), errIndex \
                and varBindTable[-1][int(errIndex)-1] or '?')
            else:
                result = []
                for var in varBindTable:
                    tempResult = {}
                    for name , val in var:
                        tempResult[name.getLabel()[len(name.getLabel())-1]] = val.prettyPrint()
                    result.append(tempResult)
                return result

测试时，我们获取到waf设备10.11.113.150的disk信息为空，其他设备可以正常获取。

流量信息
--------

也网卡或者流量相关的对象定义定义在\ `IF-MIB <http://mibs.snmplabs.com/asn1/IF-MIB>`__\ 中，可以获取的具体信息包括：

.. code:: python

    IfEntry ::=
       SEQUENCE {
           ifIndex                 InterfaceIndex,
           ifDescr                 DisplayString,
           ifType                  IANAifType,
           ifMtu                   Integer32,
           ifSpeed                 Gauge32,
           ifPhysAddress           PhysAddress,
           ifAdminStatus           INTEGER,
           ifOperStatus            INTEGER,
           ifLastChange            TimeTicks,
           ifInOctets              Counter32,
           ifInUcastPkts           Counter32,
           ifInNUcastPkts          Counter32,  -- deprecated
           ifInDiscards            Counter32,
           ifInErrors              Counter32,
           ifInUnknownProtos       Counter32,
           ifOutOctets             Counter32,
           ifOutUcastPkts          Counter32,
           ifOutNUcastPkts         Counter32,  -- deprecated
           ifOutDiscards           Counter32,
           ifOutErrors             Counter32,
           ifOutQLen               Gauge32,    -- deprecated
           ifSpecific              OBJECT IDENTIFIER -- deprecated   }

以下是获取网卡流量相关信息的示例代码：

.. code:: python


    def getIfaceTraffic(targetHost, targetPort, cmd, community, period):
        def getNowTraffic():
            errIndication, errStatus, errIndex, varBindTable = cmd.nextCmd(
                cmdgen.CommunityData(community, mpModel=1),
                cmdgen.UdpTransportTarget((targetHost,targetPort)),
                cmdgen.MibVariable('IF-MIB', 'ifDescr'), # '1.3.6.1.2.1.2.2.1.2'
                cmdgen.MibVariable('IF-MIB', 'ifInOctets'), # '1.3.6.1.2.1.2.2.1.10'
                cmdgen.MibVariable('IF-MIB', 'ifOutOctets'), #'1.3.6.1.2.1.2.2.1.16'
                #lookupValues=True,
                #lookupNames=True
            )
            if errIndication:
                print errIndication

            else:
                if errStatus:
                    print '%s at %s' % (errStatus.prettyPrint(), errIndex \
                    and varBindTable[-1][int(errIndex)-1] or '?')
                else:
                    result = []
                    #print varBindTable
                    for var in varBindTable:
                        tempResult = {}
                        for name , val in var:
                            tempResult[name.getLabel()[len(name.getLabel())-1]] = val.prettyPrint()
                        result.append(tempResult)
                    return result

        preTraffic = getNowTraffic()
        #print preTraffic
        time.sleep(period)
        afterTraffic = getNowTraffic()
        #print afterTraffic

        traffic = []
        if(len(preTraffic) != len(afterTraffic)):
            return None
        else:
            ifaceNum = len(preTraffic)
        for i in range(ifaceNum):
            if preTraffic[i]['ifDescr'] == afterTraffic[i]['ifDescr']:
                m = float(preTraffic[i]['ifInOctets'])
                mm = float(afterTraffic[i]['ifInOctets'])
                n = float(preTraffic[i]['ifOutOctets'])
                nn = float(afterTraffic[i]['ifOutOctets'])
                ifaceName = preTraffic[i]['ifDescr']
                traffic.append({
                    'ifaceName':ifaceName,
                    'inTraffic(Mbps)':(mm-m)/period/1048576*8,
                    'outTraffic(Mbps)':(nn-n)/period/1048576*8
                })
            else:
                return None
        return traffic

总结
----

``asn.1``\ 一共包括9000多个mib信息模块集合，另外我们也可以在目标机器上执行命令：

::

    snmpwalk -v 2c -c public localhost

来获取机器所能通过snmp获取的信息列表。在我的机器上运行该命令，共有近4000条mib信息。所以，我们需要从中进行甄别，获取我们所关注的所需要的信息。
