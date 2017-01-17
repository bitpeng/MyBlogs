.. _nova_interact:


nova组件间交互总结
###################


.. contents:: 目录

-----------------------

模块与组件调用关系
+++++++++++++++++++++

刚开始分析nova代码时，觉得nova组件间的交互关系非常之复杂，并且同名函数、同名类甚多，因此有时一时难以确定调用的是哪个文件、那个类。以虚机启动为例，nova-api组件在 nova/api/openstack/compute/servers.py:Controller.create 函数最终会调用self.compute_api.create发起虚机创建。当初自己是使用打日志的方式，确定self.compute_api类型，然后看对应的函数。这种方式，需要频繁打日志，重启服务，不太方便。

在熟悉nova源码后，可以发现其实组件间交互关系、api接口，还是有很强的规律性的。

首先，我们要知道，nova服务的总入口时nova-api，它是一个rest-api服务，用户不管是从horizon还是CLI发起的请求，最终都会被novaclient封装成对nova-api的http请求。其他组件之间，都是通过rpc来进行交互，涉及到的
文件，主要是api.py/rpcapi.py/manager.py。

- **rpcapi.py** ：根据之前的源码分析系列文章可以知道，除了nova-api，其他的nova组件其实都是一个rpcserver，它供其他组件调用(rpc调用)的endpoints主要由manager.py模块中的Manager类提供。rpcapi.py模块中的函数，一般(不绝对是)是发起对自身rpcserver的请求调用(即：发起cast/call请求的地方)。**该模块里的函数接口主要供本组件的api.py模块调用**

- **api.py** : 注意，该模块主要是被其他组件调用的，是其他组件和本组件交互的入口。然后接口函数一般都只是简单的调用rpcapi.py模块中对应的同名方法。

- **manager.py**: 还是由之前的源码分析文章可知，rpc服务启动时，使用manager.py模块中的Manager类、BaseRPCApi类构成rpc endpoints并创建rpc-server，监听队列，等待其他组件发起请求。

如虚机创建的前两个阶段(该图使用graphviz绘)：

.. figure:: /_static/images/nova1.png
   :scale: 100
   :align: center

   虚机创建的前两个阶段调用关系

如 nova-api 尝试对 nova-conductor 发起rpc调用时，并不会直接调用 nova/conductor/rpcapi.py 发起
cast rpc调用，而是调用 nova/conductor/api.py，然后在api.py模块中调用rpcapi.py模块中的同名函数，
而rpcapi.py模块才最终发起rpc请求。rpc请求由 nova/conduct/manager.py中的endpoints处理。


一些误区
+++++++++

原来自己误认为，属于某个目录下(如:nova/compute)的代码，就是某个组件的。比如自己看日志时，nova-api直接调用了nova/compute/api.py模块下的函数，以为该模块里的log日志是输出到nova-compute.log里，结果怎么都找不到。实际上，组件执行时，除非发生异常，否则直到发起rpc调用的地方，都是属于该组件(进程)的代码。



