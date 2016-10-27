.. _horizon_launch_instance:


########################
horizon启动虚拟机分析
########################



..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


.. note::

    本篇文章分析OpenStack通过horizon启动虚拟机的流程。


.. contents:: 目录

--------------------------


步骤
=====

-   URLs.py URL映射

    .. figure:: /_static/images/Launch_instance_url.png
       :scale: 100
       :align: center

       启动虚拟机URL映射

-   启动虚拟机workflow

    ::

        class LaunchInstanceView(workflows.WorkflowView):
            # 启动虚拟机的workflow
            workflow_class = project_workflows.LaunchInstance
            
            # 传递给LaunchInstance workflow 的初始值
            def get_initial(self):
                initial = super(LaunchInstanceView, self).get_initial()
                initial['project_id'] = self.request.user.tenant_id
                initial['user_id'] = self.request.user.id
                return initial
           
-   接下来，在workflow中，一共有五个steps，其中，第一个步骤设置permissions
    而进行隐藏。它的主要作用是贡献两个字段让后面的步骤进行依赖，从而对后面的steps进行校验。 

    下面有一个单独小节，说明启动虚拟机和workflow中的一些要点。

启动虚拟机workflow
+++++++++++++++++++


#.  启动虚拟机工作流中，五个steps中第一个通过设置permissions进行隐藏，它的主要
    作用是贡献两个字段让后面的步骤进行依赖(depends_on)，从而对后面的steps中Action(表单)数据进行校验。 

    
#.  每一个step都可以贡献数据(贡献的数据对workflow的handle函数可见。)。其中，从action表单中定义的
    字段自动可见，但是其他字段，需要通过contribulte函数手动添加到context 字典中。
    
    如：SetInstanceDetails步骤贡献了source_type字段，但是该字段在SetInstanceDetails Step的action类SetInstanceDetailsAction中并没有定义，需要在contribute函数中手动更新。

    .. figure:: /_static/images/step_contribute.png
       :scale: 100
       :align: center

       contribute函数手动添加非在action中定义的contributions


#.  Action父类有一个_populate_choices方法，会调用所有的"populate_%s_choices"函数，所以Action类中
    "populate_%s_choices" 函数的作用是动态获取下拉列表可供选择的选项数据。

    .. figure:: /_static/images/_populate_choices.png
       :scale: 100
       :align: center

       Action 类的_populate_choices方法

    .. figure:: /_static/images/populate_s_choices.png
       :scale: 100
       :align: center

       "populate_%s_choices" 系列函数


#.  调用handle方法。首先会调用workflow的所有steps的Action类的handle方法，workflow类的handle方法最后调用。
    
    **另外，在每一个step中列出的所有"contributes="和"depends_on="字段都是可用的, 我们可以通过handle方法的第三个字典参数引用之。**

    .. figure:: /_static/images/workflow_handle.png
       :scale: 100
       :align: center

       workflow 的handle方法
       

#.  调用openstack_dashboard api函数创建虚拟机：

    .. figure:: /_static/images/call-server_create.png
       :scale: 100
       :align: center

       调用api创建虚拟机


未完待续……



	   

   
---------------------

参考
=====

.. [#] http://f.dataguru.cn/thread-127360-1-1.html
.. [#] http://askubuntu.com/questions/140360/kvm-kernel-module-error

