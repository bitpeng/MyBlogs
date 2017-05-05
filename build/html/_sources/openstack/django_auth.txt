.. _django_auth:


Django认证：horizon登录认证解析
################################

**date: 2017-04-25 17:11**

.. contents:: 目录

--------------------------

在我之前的文章《django中间件和用户重登陆分析》中，分析了Django中间件并简要分析分析了openstack horizon用户登录流程，
最近深究这个模块时，发现这里面也大有学问，涉及到的知识点也很多，自己对horizon登录认证这一部分，
也分析了好久，才算有一个比较深刻的认识，而之前写的那篇文章，有很大的知识点错误，现在另起一篇博文，进行分析。

下面对用户登录horizon的流程和Django认证backend流程记录下来，并会简要分析django认证框架相关实现代码。
由于主要关注的是Django认证过程，相关无关部分会忽略掉。

url映射
=======

用户输入IP地址，根据setting.py ROOT_URLCONF配置项来决定根URL映射函数；

.. figure:: /_static/images/root_urlconf.png
    :scale: 100
    :align: center

    openstack_dashboard/setting.py ROOT_URLCONF 配置项

然后，根据URL匹配调用view处理函数(splash函数。)

.. figure:: /_static/images/url_map.png
    :scale: 100
    :align: center

    openstack_dashboard/urls.py


注意：ROOT_URLCONF配置项很重要，整个URL只能匹配该urls.py所指定的。
假如我们输入一个正则无法匹配的，就会提示如下错误：

.. figure:: /_static/images/page_not_found.png
    :scale: 100
    :align: center

    url模式

根据上图中所列出的URL模式，可以看到所有可匹配URL都是由root urls.py文件决定。
需要注意的是urls.py中的include模式。

然后根据request session判断用户是否认证(请求中间件拦截，判断是否会话失效，这里不予考虑)，
如果认证，则重定向到用户主界面；否则就加载模板系统，显示登录主界面；

.. figure:: /_static/images/splash.png
    :scale: 100
    :align: center

    openstack_dashboard/views.py

.. figure:: /_static/images/splash_html.png
    :scale: 100
    :align: center

    horizon/templates/splash.html 模板include表单模板

用户登录认证
==============

.. important::

    原来自己写的表单校验与用户认证流程有重大错误。整个认证流程，自己通过不断的打日志和代码分析，
    已经完全理解清晰。下面对整个过程进行更新！
    
表单处理程序
+++++++++++++

显示登录主界面后，用户输入信息，提交表单，根据表单action属性匹配映射处理函数。

.. figure:: /_static/images/form_action.png
    :scale: 100
    :align: center

    登录页面，表单action属性。

.. note::

    _login.html 表单继承 model_from1.html，并重写action 属性，但是{% url 'login' %} 最后怎么转换成"auth/login"，
    还需要进一步的分析。

    .. figure:: /_static/images/model_form1.png
        :scale: 100
        :align: center

        基类表单模板action属性

    .. figure:: /_static/images/model_form1.png
        :scale: 100
        :align: center

        _login.html 模板表单重写action 属性

.. tip::

    上面提到的{% url 'login' %}最后怎么转换成"auth/login"的过程已经理清，这里涉及到django中的name参数。
      
    .. code-block:: python

        # openstack_auth/urls.py
        urlpatterns = patterns(
            'openstack_auth.views',
            url(r"^testlogin/$", "login", name='dlogin'),

    .. figure:: /_static/images/testlogin.png
        :scale: 100
        :align: center

        页面显示代码

    ::

        # 魔板文件重写form_action属性！
        {% block form_action %}{% url 'dlogin' %}{% endblock %}


    页面模板使用{%url 'dlogin' %}转换url，所以总是转换成该名字对应的URL。
  
    .. [#] 论述了django URL name参数的用法及其意义。http://www.cnblogs.com/no13bus/p/3767521.html


表单处理URL映射过程
++++++++++++++++++++

表单映射过程的URL截断，分级URL匹配。

.. figure:: /_static/images/url_include_1.png
    :scale: 100
    :align: center

    URL include 截断匹配

.. figure:: /_static/images/auth_url.png
    :scale: 100
    :align: center

    URL分级匹配

.. important::

    每当Django遇到 include() 时，它将截断匹配的URL，并把剩余的字符串发往包含的URLconf作进一步处理。

    include 通常用于网站目录分类处理，使项目中urls高度统一。
    
表单处理程序
++++++++++++++

这里为了便于分析，我把整个登录提交表单对应的处理代码贴出来。

:file: `openstack_auth/views.py:login`

.. code-block:: python
    :linenos:

    @sensitive_post_parameters()
    @csrf_protect
    @never_cache
    def login(request, template_name=None, extra_context=None, **kwargs):
        """Logs a user in using the :class:`~openstack_auth.forms.Login` form."""
        # If the user is already authenticated, redirect them to the
        # dashboard straight away, unless the 'next' parameter is set as it
        # usually indicates requesting access to a page that requires different
        # permissions.
        #LOG_DEBUG(info=locals())
        LOG_DEBUG(request.user)
        if (request.user.is_authenticated() and
                auth.REDIRECT_FIELD_NAME not in request.GET and
                auth.REDIRECT_FIELD_NAME not in request.POST):
            return shortcuts.redirect(settings.LOGIN_REDIRECT_URL)

        # Get our initial region for the form.
        initial = {}
        current_region = request.session.get('region_endpoint', None)
        requested_region = request.GET.get('region', None)
        regions = dict(getattr(settings, "AVAILABLE_REGIONS", []))
        if requested_region in regions and requested_region != current_region:
            initial.update({'region': requested_region})

        if request.method == "POST":
            # NOTE(saschpe): Since https://code.djangoproject.com/ticket/15198,
            # the 'request' object is passed directly to AuthenticationForm in
            # django.contrib.auth.views#login:
            if django.VERSION >= (1, 6):
                form = functional.curry(forms.Login)
            else:
                form = functional.curry(forms.Login, request)
        else:
            form = functional.curry(forms.Login, initial=initial)

        if extra_context is None:
            extra_context = {'redirect_field_name': auth.REDIRECT_FIELD_NAME}

        if not template_name:
            if request.is_ajax():
                template_name = 'auth/_login.html'
                extra_context['hide'] = True
            else:
                template_name = 'auth/login.html'

        LOG_DEBUG(request.user, user_type=type(request.user)) 
        LOG_DEBUG(template_name=template_name,
                  authentication_form=form,
                  extra_context=extra_context,
                  kw=kwargs)     
        res = django_auth_views.login(request,
                                      template_name=template_name,
                                      authentication_form=form,
                                      extra_context=extra_context,
                                      **kwargs)
        # Set the session data here because django's session key rotation
        # will erase it if we set it earlier.
        LOG_DEBUG(request.user, user_type=type(request.user))
        if request.user.is_authenticated():
            auth_user.set_session_from_user(request, request.user)
            regions = dict(forms.Login.get_region_choices())
            region = request.user.endpoint
            region_name = regions.get(region)
            request.session['region_endpoint'] = region
            request.session['region_name'] = region_name
        LOG_DEBUG(info=locals())
        return res

这里的关键是第51行代码 ``res = django_auth_views.login(request,`` ，
调用这个函数时，会把登录表单类实例作为参数。然后在 :func:`django.contrib.auth.login` 函数里面，
会调用 ``openstack_auth.forms.Login:clean()`` 方法，请看clean方法的调用堆栈：

.. figure:: /_static/images/clean_call_stack.png
    :scale: 100
    :align: center

    登录表单forms的clean()方法调用堆栈

**登录表单重写的clean方法一方面会执行数据校验，然后会根据输入的用户名和密码，
进行用户认证(会调用keystone认证后端，后面会详细描述)。**

:file:`openstack_auth/forms:Login.clean`

.. code-block:: python
    :linenos:

    @sensitive_variables()
    def clean(self):
        LOG_DEBUG('add clean here?')
        LOG_STACK()
        default_domain = getattr(settings,
                                 'OPENSTACK_KEYSTONE_DEFAULT_DOMAIN',
                                 'Default')
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        region = self.cleaned_data.get('region')
        domain = self.cleaned_data.get('domain', default_domain)

        #get usbkey sn add by wuzhifan@cecgw.cn at 2014-6-19
        usbkey = self.cleaned_data.get('usbkey')

        if not (username and password):
            # Don't authenticate, just let the other validators handle it.
            return self.cleaned_data
        ### add by zhaoyuanjie
        client_ip = ''
        if self.request.META.has_key('HTTP_X_FORWARDED_FOR'):
            client_ip = self.request.META['HTTP_X_FORWARDED_FOR']
        else:
            client_ip = self.request.META['REMOTE_ADDR']

        # cec: get login failed times
        login_cnt = models.CECUserLoginCnt.get_login_cnt(username, client_ip)

        # cec:
        if login_cnt >=3:
            raise forms.ValidationError(_('User login failed more than 3 times, please try again later!'))
        # add by zhaoyuanjie
        # add by wangxing@cecgw.cn for time access control to users 
        LOG.info("Is true or false: %s" %Acl_user.in_user_access_timerange(username))
        if not Acl_user.in_user_access_timerange(username):
            raise forms.ValidationError(_("The user's current time cannot access system!"))
        # add end

        try:
            LOG_DEBUG(username=username,
                       password=password,
                       user_domain_name=domain,
                       auth_url=region,
                       usbkey=usbkey)
            self.user_cache = authenticate(request=self.request,
                                           username=username,
                                           password=password,
                                           user_domain_name=domain,
                                           auth_url=region,
                                           usbkey=usbkey)  #add by wuzhifan@cecgw.cn at 2014.11.15
            LOG_DEBUG(user_cache=self.user_cache, user_type=type(self.user_cache))
            LOG_DEBUG(backend=self.user_cache.backend)
            msg = 'Login successful for user "%(username)s".' % \
                {'username': username}
            LOG.info(msg)
            m = "[%s] " % log_common.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + \
                log_common.LOG_TYPE + u" [用户:%s] 登陆IP:%s [登陆系统] %s %s" \
                % (username, client_ip, log_common.STATUS_SUCCESS, self.user_cache.tenant_id)
            ceclog.info(m)
        except exceptions.KeystoneAuthException as exc:
            msg = 'Login failed for user "%(username)s".' % \
                {'username': username}
            LOG.warning(msg)
            m = "[%s] " % log_common.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + \
                log_common.LOG_TYPE + u" [用户:%s] 登陆IP:%s [登陆系统] %s" \
                % (username, client_ip, log_common.STATUS_FAIL)
            ceclog.error(m)

            # cec: update login failed times
            models.CECUserLoginCnt.update_login_cnt(username,
                   client_ip, login_cnt+1)
            # add by zhaoyuanjie
            self.request.session.flush()
            raise forms.ValidationError(exc)
        if hasattr(self, 'check_for_test_cookie'):  # Dropped in django 1.7
            self.check_for_test_cookie()
        return self.cleaned_data

.. note::

    - 表单数据检验，注意可以使用clean_message方法来校验每一个表单属性，也可以使用clean 方法整体校验。
    - 表单校验clean函数，需要返回原始数据(cleaned_data)，否则会发生数据丢失。

django认证后端
+++++++++++++++

登录表单forms的clean方法，在第45行 ``self.user_cache = authenticate(request=self.request,`` 这一处代码中，
会执行用户认证。查看 :func:`authenticate` 函数代码，实际上该函数会调用settings.py配置的认证后端：


.. figure:: /_static/images/auth_backend.png
    :scale: 100
    :align: center

    setting.py认证后端项

:file: `django.contrib.auth.__init__`

.. code-block:: python
    :linenos:

    def get_backends():
        backends = []
        for backend_path in settings.AUTHENTICATION_BACKENDS:
            backends.append(load_backend(backend_path))
        if not backends:
            raise ImproperlyConfigured(
                       'No authentication backends have been defined. Does AUTHENTICATION_BACKENDS contain anything?')
        return backends

    def authenticate(**credentials):
        """
        If the given credentials are valid, return a User object.
        """
        for backend in get_backends():
            try:
                user = backend.authenticate(**credentials)
            except TypeError:
                # This backend doesn't accept these credentials as arguments. Try the next one.
                continue
            except PermissionDenied:
                # This backend says to stop in our tracks - this user should not be allowed in at all.
                return None
            if user is None:
                continue
            # Annotate the user object with the path of the backend.
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            return user

        # The credentials supplied are invalid to all backends, fire signal
        user_login_failed.send(sender=__name__,
                credentials=_clean_credentials(credentials))


从 :func:`authenticate` 函数的实现来看，Django可以配置多个认证后端。
然后按照顺序，依次调用每一个认证后端，知道找到第一个认证成功/失败的后端，
该函数才退出！

至此，整个用户登录的流程，已经完全清晰了。


---------------------

参考
=====

.. [#] http://djangobook.py3k.cn/2.0/chapter17/
.. [#] http://lukejin.iteye.com/blog/599783
.. [#] http://www.52ij.com/jishu/1174.html
.. [#] http://www.cnblogs.com/daoluanxiaozi/p/3320618.html
.. [#] http://www.nowamagic.net/academy/detail/13281811

