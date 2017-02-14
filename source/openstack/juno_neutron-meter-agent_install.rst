.. _install_neutron_meter_agent:


################################
juno安装neutron-meter-agent
################################


.. contents:: 目录

--------------------------

老大叫我调研下neutron-metering-agent，为后期可能的监控项目做知识储备，由于
所部署环境是基于比较老的版本(juno)，安装时还是遇到一定的困难，现在对在openstack juno版本
下安装neutron-metering-agent过程简单记录下。


apt-get 尝试
=============


首先尝试直接使用apt-get方式安装，结果提示包依赖版本不匹配。这里有意思的是，是所依赖的包neutron-common版本过高。

.. figure:: /_static/images/install_neutron_meter.png
   :scale: 100
   :align: center

   提示包依赖版本不匹配

尝试更新源列表，把juno源加入到source.list 文件，然后再次尝试安装。可能由于GFW缘故，提示有些源无法连接上，安装再次失败。

不得已，于是准备下载deb包，尝试手动安装。通过google很快找到了 ``1:2014.1.3-0ubuntu1.1`` 版本neutron-metering-agent的连接：
`neutron-metering-agent连接 <https://www.ubuntuupdates.org/package/core/trusty/universe/security/neutron-metering-agent>`_

下载好deb包后，然后使用 dpkg -i 手动安装，结果依然出现相同的包依赖问题。

既然包版本不匹配，于是尝试降级安装neutron-common的低版本，结果更多的neutron-agent组件出现依赖问题。
哈哈，已经快疯了！

.. figure:: /_static/images/install_pkg_version.png
   :scale: 100
   :align: center

   安装neutron-common的低版本！

手动下载2014.2.1版本并安装
============================

看来只有尝试手动下载和neutron-common_2014.2.1相同版本的neutron-metering-agent了。由于不知道确切的版本号，于是
只有根据neutron-common版本号搜索，很快也通过google找到了版本为 ``1:2014.2.1-0ubuntu1~cloud0`` 的所有neutron相关的包：
`neutron_2014.2.1连接 <https://launchpad.net/~openstack-ubuntu-testing/+archive/ubuntu/juno/+build/6648524>`_

然后选择下载neutron-metering-agent_2014.2.1-0ubuntu1~cloud0_all.deb。并使用dpkg -i 命令直接安装，终于一切正常。

.. figure:: /_static/images/neutron_agent.png
   :scale: 100
   :align: center

   metering-agent状态正常

---------------------

参考
=====

.. [#] https://launchpad.net/~openstack-ubuntu-testing/+archive/ubuntu/juno/+build/6648524
.. [#] https://launchpad.net/ubuntu/trusty/+package/neutron-common
