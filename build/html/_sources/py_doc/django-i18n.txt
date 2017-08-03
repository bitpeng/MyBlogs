.. _django-tip:


django国际化
#############


.. contents:: 目录

--------------------------

在高安云开发中，一般通过rest-api接口获取的数据都是json格式的Unicode字符串。在前端展示时，
可能需要翻译/转化成对应的中文格式。因此，前段时间，调研了下Django框架的国际化问题。
下面的文档通过小例子，来说明Django国际化中的涉及到的点。

需要注意的是，在调研的时候，参考了一些网络文档，可是由于Django版本的原因，
网上给出的实例代码并不能正确的执行，费了较大功夫才调试正确。
下面的例子，在我的测试环境中运行没有问题，django版本为"1.6.1"，对于其他版本，部分细节可能需要修改。

.. code-block:: console

    root@allinone-v2:/smbshare/testi18n# django-admin --version
    1.6.1

有关国际化和本地化的相关概念，大家可以参考有关文档。

Python代码国际化
=================

首先开启一个新的Django项目并新建一个APP：

::

    cd /smbshare/
    django-admin startproject testi18n
    django-admin startapp app1
    
编辑app1的视图文件views.py，增加如下代码：

::

    #coding:utf-8

    from django.shortcuts import render
    from django.utils.translation import ugettext as _

    # Create your views here.
    from django.http import HttpResponse
    import time

    def test1_view(request):
        # 获得系统本地时间，返回的格式是 UTC 中的 struct_time 数据
        t  = time.localtime()
        # 第 6 个元素是 tm_wday , 范围为 [0,6], 星期一 is 0
        n  = t[6]
        # 星期一到星期日字符串
        weekdays = [_('Monday'), _('Tuesday'), _('Wednesday'),
                    _('Thursday'), _('Friday'), _('Saturday'), _('Sunday')]
        # 返回一个 HttpResponse、，这段代码将用来返回服务器系统上是星期几。
        return HttpResponse(weekdays[n])

然后在root urls文件中加入对应的URL：

::

    from app1 import views as app1_views

    urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'testi18n.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),

        url(r'^admin/', include(admin.site.urls)),

        url(r'^app1$', app1_views.test1_view),
    )
    
启动web服务，并在浏览器进行测试，此时应该可以看到英文的星期了。

现在我们想对英文星期进行翻译，首先要对需要翻译的文本进行标记，然后创建语言文件。
我们在上面的views文件中，已经通过_下划线(ugettext函数的别名)对需要翻译的文本进行标记了。

在项目目录下创建locale文件。

::

    cd /smbshare/testi18n
    mkdir locale
    django-admin makemessages -l zh_CN

然后编辑 locale/zh_CN/LC_MESSAGES/django.po文件，并编译信息文件：

::

    #: app1/views.py:22
    msgid "Monday"
    msgstr "星期1"

    #: app1/views.py:22
    msgid "Tuesday"
    msgstr "星期2"

    #: app1/views.py:22
    msgid "Wednesday"
    msgstr "星期3"

    #: app1/views.py:23
    msgid "Thursday"
    msgstr "星期4"

    #: app1/views.py:23
    msgid "Friday"
    msgstr "星期5"

    #: app1/views.py:23
    msgid "Saturday"
    msgstr "星期6"

    #: app1/views.py:23
    msgid "Sunday"
    msgstr "星期7"

::

    django-admin compilemessages

然后在settings.py文件中，配置相关的国际化选项：

::

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

请注意注意MIDDLEWARE_CLASSES中的'django.middleware.locale.LocaleMiddleware', 需要放在'django.contrib.sessions.middleware.SessionMiddleware'后面。

然后在浏览器中重新打开页面，看到翻译效果了：

.. figure:: /_static/images/i18n_app1.png
   :scale: 100
   :align: center

   国际化效果

.. important::

    实际上，假如在settings.py文件中，配置了有关国际化选项后，即使没有编辑django.po语言文件，
    刷新页面，还是可以看到中文效果，这一点刚开始我也是有点疑惑。后来，参考了官方文档，
    这和Django查找翻译文件的顺序机制有关：
    
    - 首先，会通过settings.py文件中配置的LOCALE_PATHS(后面会再次提到该配置项)选项查找翻译文件；
    - 然后在每个app目录下查找：$APPPATH/locale/<language>/LC_MESSAGES/django.(po|mo)
    - 然后在django conf文件中查找：$PYTHONPATH/django/conf/locale/<language>/LC_MESSAGES/django.(po|mo)
    
    .. [#] https://docs.djangoproject.com/en/1.11/topics/i18n/translation/#how-django-discovers-translations

    回到这个例子本身，即使没有编辑django.po语言文件，但是最终还是会查找django库conf中的中文翻译文件，
    并加载显示中文化效果。
    
    .. figure:: /_static/images/django_conf.png
       :scale: 100
       :align: center


模板国际化
===============

新建一个APP，测试Django模板国际化：

::

    django-admin startapp app2

在项目目录下新建templates/app2/index.html，模板内容如下：

::

    {% load i18n %}

    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{{ LANGUAGE_CODE }}" lang="{{ LANGUAGE_CODE }}">

    <head>
       <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
       <title>Welcome to my site</title>
            <script  type="text/javascript">
                  function selectdo(obj) {
                           str="/i18n/setlang/";
                           myform = document.getElementById('testform');
                           myform.method = "POST";
                           myform.action = str;
                           myform.submit();
                   }
           </script>
    </head>
    <body>
           <form name="testform" id="testform" method='post'>
               {% csrf_token %}
               <select id="language" name="language" onchange="selectdo(this)">
              <!--    <input name="next" type="hidden" value="{{request.path}}" />-->
                   <option value="1" >{% trans "Languages" %}</option>
                    {% for lang in LANGUAGES %}
                   <option value="{{ lang.0 }}" > {{ lang.1 }}</option>
                    {% endfor %}
                 </select>
            </form>
            <p>{% trans "The first sentence is from the  template index.html" %}</p>
           {{ code }}
    </body>
    </html>

需要注意的几点：

- 注意要加入 {% load i18n %}；
- 表单中加入 {% csrf_token %}，否则语言切换时会提示错误；
- 将 testform 的 action 重定向到 /i18n/setlang/，
  启用了 django.views.i18n.set_language视图，它的作用是设置用户语言偏好并重定向返回到前一页面；

然后在settings.py中设置模板路径：

::

    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_DIRS = (
        os.path.join(os.path.dirname(ROOT_PATH), 'templates'),
    )

然后编辑app2视图文件，变更新url。

:file:`app2/views.py`
::

    from django.shortcuts import render

    # Create your views here.

    # Create your views here.
    from django.http import HttpResponse
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    from django.utils.translation import ugettext_lazy as _

    def test2_view(request):
       code = _("The second sentence is from the Python code.");
       responseContext = {'lang':request.LANGUAGE_CODE,
                          'code':code,
                         }
       resp = render_to_response('app2/index.html', responseContext,
                                   context_instance=RequestContext(request))
       return resp

:file:`testi18n/urls.py`   
::

    from django.conf.urls import patterns, include, url

    from app1 import views as app1_views
    from app2 import views as app2_views

    from django.contrib import admin
    admin.autodiscover()

    urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'testi18n.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),

        url(r'^admin/', include(admin.site.urls)),

        url(r'^app1$', app1_views.test1_view),
        url(r'^app2$', app2_views.test2_view),
        url(r'^i18n/', include('django.conf.urls.i18n')),
    )

更新国际化的相关配置，特别需要注意的是，TEMPLATE_CONTEXT_PROCESSORS选项，
需要加上'django.contrib.auth.context_processors.auth'，否则浏览页面会发生异常。

::

    ugettext = lambda s: s

    LANGUAGES = (
       ('en-us', ugettext('English')),
       ('zh-CN', ugettext('Chinese')),
    )

    TEMPLATE_CONTEXT_PROCESSORS = (
        #"django.core.context_processors.auth",
        'django.contrib.auth.context_processors.auth',
        #"django.core.context_processors.debug",

        "django.core.context_processors.i18n",
        #"django.core.context_processors.request",
    )

    LOCALE_PATHS = (
        #os.path.join(BASE_DIR, 'locale'),
        os.path.join(os.path.dirname(ROOT_PATH), 'locale'),
    )

这里需要注意，需要用数据库保存session。执行下面命令， 产生 django_session 数据表。

::

    python manage.py syncdb

更新语言文件并翻译：

::

	#: app2/views.py:12
	msgid "The second sentence is from the Python code."
	msgstr "这句话来自于Python代码"

	#: templates/app2/index.html:23
	msgid "Languages"
	msgstr "语言"

	#: templates/app2/index.html:29
	msgid "The first sentence is from the  template index.html"
	msgstr "这句话来自于模板index.html"

	#: testi18n/settings.py:96
	msgid "English"
	msgstr "英文"

	#: testi18n/settings.py:97
	msgid "Chinese"
	msgstr "中文"

::

    django-admin compilemessages

然后浏览页面，刚开始怎么都看不到翻译的效果。后来，查找了大量的文档，在配置项中，
加上LOCALE_PATHS(在前文中提到过该配置项和Django语言文件查找机制)：

::

	LOCALE_PATHS = (
		#os.path.join(BASE_DIR, 'locale'),
		os.path.join(os.path.dirname(ROOT_PATH), 'locale'),
	)

再次刷新页面，然后就可以看到国际化的效果了。

.. figure:: /_static/images/i18n_zhongwen.png
   :scale: 100
   :align: center
   
.. figure:: /_static/images/i18n_en.png
   :scale: 100
   :align: center

可是，参考openstack horizon项目，我并没有在项目settings.py配置文件中，
发现LOCALE_PATHS这个配置项，但是openstack dashboard还是可以中文汉化显示，
这个问题以及Django国际化的很多细节，待以后进一步深究。


---------------------

参考
=====

.. [#] 主要参考了这篇文章，可是由于django版本的原因，复制该文章的代码，并不能直接运行，很多细节和配置项需要修改。
       网址：https://www.ibm.com/developerworks/cn/web/1101_jinjh_djangoi18n/
.. [#] django国际化官方参考手册。
       网址：https://docs.djangoproject.com/en/1.11/topics/i18n/translation/#how-django-discovers-translations
