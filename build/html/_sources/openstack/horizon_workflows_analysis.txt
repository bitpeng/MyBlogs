.. _horizon_workflows:


[翻译] horizon workflows分析
############################


.. tip::

    - 这篇文章以openstack Havana版本"编辑虚拟机"项对openstack horizon工作流进行分析；
    - 阅读相关参考资料的过程中，尽量阅读官网或者英文文档。比如horizon workflow机制，
      官网英文并不难理解，倒是在参考中文资料的过程中，由于翻译晦涩甚至翻译错误，反而难以理解。


构建引人注目的用户体验最具挑战性的方面之一是制作复杂的多部分工作流。 
Horizon的工作流模块旨在将该功能带入日常生活。 


workflows
=========

workflows是复杂的包括多tab的表单。每一个workflow包括一系列继承 ``Workflow`` ， ``Step`` 和 ``Action`` 的类。


一个workflow的复杂例子
++++++++++++++++++++++

下面是一个复杂例子，它阐述了数据怎样在urls、views、workflows和templates之间交换。


#.  在urls.py中，我们包括一个命名参数(正则表达式命名元组)。如：resource_class_id.

    ::

        RESOURCE_CLASS = r'^(?P<resource_class_id>[^/]+)/%s$'

        urlpatterns = [
            url(RESOURCE_CLASS % 'update', UpdateView.as_view(), name='update')
        ]

#.  在views.py中，我们把数据传递给templates和action(是一种表单)。 
    (action也可以传递数据到 ``get_context_data`` 函数和传到templates上。)


    ::

        class UpdateView(workflows.WorkflowView):
            workflow_class = UpdateResourceClass

            def get_context_data(self, **kwargs):
                context = super(UpdateView, self).get_context_data(**kwargs)
                # Data from URL are always in self.kwargs, here we pass the data
                # to the template.
                # URL参数传递的数据一般在self.kwargs中，我们把它传递给模板；
                context["resource_class_id"] = self.kwargs['resource_class_id']
                # Data contributed by Workflow's Steps are in the
                # context['workflow'].context list. We can use that in the
                # template too.
                # 由workflow's Step贡献的数据在context['workflow'].context列表中，我们在模板中也可以使用。
                return context

            def _get_object(self, *args, **kwargs):
                # Data from URL are always in self.kwargs, we can use them here
                # to load our object of interest.
                # URL参数传递的数据一般在self.kwargs中，我们可以通过它加载一些对象。
                resource_class_id = self.kwargs['resource_class_id']
                # Code omitted, this method should return some object obtained
                # from API.
                # 通过id获取对象，并返回，代码略。

            def get_initial(self):
                resource_class = self._get_object()
                # This data will be available in the Action's methods and
                # Workflow's handle method.
                # But only if the steps will depend on them.
                # 假如steps depends_on这些数据，那么这些数据可以在Action的函数和workflow 的handle函数中使用。
                return {'resource_class_id': resource_class.id,
                        'name': resource_class.name,
                        'service_type': resource_class.service_type}


#.  在 workflows.py中，我们处理数据，它仅仅是一个更复杂的表单而已。

    ::

        class ResourcesAction(workflows.Action):
            # The name field will be automatically available in all action's
            # methods.
            # If we want this field to be used in the another Step or Workflow,
            # it has to be contributed by this step, then depend on in another
            # step.
            name = forms.CharField(max_length=255,
                                   label=_("Testing Name"),
                                   help_text="",
                                   required=True)

            def handle(self, request, data):
                pass
                # If we want to use some data from the URL, the Action's step
                # has to depend on them. It's then available in
                # self.initial['resource_class_id'] or data['resource_class_id'].
                # In other words, resource_class_id has to be passed by view's
                # get_initial and listed in step's depends_on list.

                # We can also use here the data from the other steps. If we want
                # the data from the other step, the step needs to contribute the
                # data and the steps needs to be ordered properly.

        class UpdateResources(workflows.Step):
            action_class = ResourcesAction
            # This passes data from Workflow context to action methods
            # (handle, clean). Workflow context consists of URL data and data
            # contributed by other steps.
            depends_on = ("resource_class_id",)

            # By contributing, the data on these indexes will become available to
            # Workflow and to other Steps (if they will depend on them). Notice,
            # that the resources_object_ids key has to be manually added in
            # contribute method first.
            contributes = ("resources_object_ids", "name")

            def contribute(self, data, context):
                # We can obtain the http request from workflow.
                request = self.workflow.request
                if data:
                    # Only fields defined in Action are automatically
                    # available for contribution. If we want to contribute
                    # something else, We need to override the contribute method
                    # and manually add it to the dictionary.
                    # 只有Action中定义的fields可用。如果要使得其他东西可用，
                    # 需要重写contribute函数并手动更新context字典；
                    context["resources_object_ids"] =\
                        request.POST.getlist("resources_object_ids")

                # We have to merge new context with the passed data or let
                # the superclass do this.
                context.update(data)
                return context

        class UpdateResourceClass(workflows.Workflow):
            default_steps = (UpdateResources,)

            def handle(self, request, data):
                pass
                # This method is called as last (after all Action's handle
                # methods). All data that are listed in step's 'contributes='
                # and 'depends_on=' are available here.
                # It can be easier to have the saving logic only here if steps
                # are heavily connected or complex.

                # data["resources_object_ids"], data["name"] and
                # data["resources_class_id"] are available here.


---------------------

参考
=====

.. [#] http://docs.openstack.org/developer/horizon/topics/workflows.html
.. [#] http://docs.openstack.org/developer/horizon/ref/workflows.html
