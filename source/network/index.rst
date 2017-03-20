.. _network:


网络技术/neutron
=================

**date: 2017-2-24 11:20**

这一栏是网络技术相关笔记，包括传统的TCP/IP网络技术和新型网络技术：主要包括云技术网络虚拟化、OpenStack neutron项目和SDN等。

写这一栏目相关文章也有些渊源，本来年前nova项目分析告一段落之后，本想继续开始cinder项目分析的。
nova/cinder/neutron作为OpenStack的三个核心项目，分别解决了云计算环境下的计算、存储、网络等问题，
而neutron号称是openstack复杂性最高的项目，我对它一直是感觉敬而远之。
(初次学习光是一堆陌生的术语br-int/br-ex/gre/vlan/iptables/tap/tun/veth等就已经让人头疼不已了)。
可因为项目需要，调研了下neutron-metering-agent组件，并想进一步深究该组件实现原理，
于是学习了下iptables/linux network namespace，并一发不可收拾。

其实，我要写的东西，可能网上相关文章一搜一大把，可是我还是决定自己动手写总结，
自己写一遍和把别人的文章看N遍，理解和把握上肯定是不一样的。

BTW，自己学习时也参考了网络上的很多材料，中英文的都有，很多写的很好，但是有些却有很明显的错误。
可能我写的也是如此，请大家注意甄别！并欢迎指正。

.. toctree::
    :maxdepth: 3
    :numbered: 3

    net_dev
    neutron_intro

..    neutron_server_start

