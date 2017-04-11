
Ceph web管理/监控平台Inkscope部署
##################################


.. contents:: 目录

--------------------------

- Linux环境：ubuntu-14.04-LTS

  * IP：192.168.159.155/20.20.20.20/10.10.10.10
- 系统环境：juno-all-inone
- ceph集群：

  * 一个mon/一个mds/三个osd
  * mon-addr: 20.20.20.20:6789

这篇文章主要参考了 `inkScope部署手册 <http://cloud.51cto.com/art/201507/486005.htm>`_ ；

基本上，按照该配置教程，基本上就可以安装成功。这篇文章，尝试把安装过程中遇到的问题以及简要安装过程记录下来。


下载deb包
==========

由于是基于ubuntu部署，首先需要下载inkscope相关deb包。
可以从github上 `inkscope package <https://github.com/inkscope/inkscope-packaging/tree/master/DEBS>`_ 直接下载。


安装相关依赖
=============

::

    apt-get install python-pip apache2 libapache2-mod-wsgi mongodb python-ceph
    pip install flask requests simplejson
    # 直接安装下载的deb包
    dpkg -i inkscope-admviz_1.2.0-0.deb  inkscope-common_1.2.0-0.deb inkscope-sysprobe_1.2.0-0.deb


配置apache2服务
===============

安装完inkscope-admviz后默认虚拟主机配置文件位于/etc/httpd/conf.d/inkScope.conf，
将其拷贝到/etc/apache2/sites-available中。修改32行为下面这句，注释掉33行

::

    ProxyPass /ceph-rest-api/ http://20.20.20.20:5000/api/v0.1/
    #ProxyPass /shell http://$IP:4200/


同时将25和35行的ErrorLog和CustomLog的值里面的httpd修改为apache2，因为apache2的工作路径已经换了。

修改 /etc/apache2/ports.conf 文件，增加下面

::

    Listen 8080
    NameVirtualHost *:8080

完整inkScope.conf文件如下：

::

    <VirtualHost *:8080>
        ServerName  localhost
        ServerAdmin webmaster@localhost

        DocumentRoot /var/www/inkscope
        <Directory "/var/www/inkscope">
            Options All
            AllowOverride All
        </Directory>

        ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
        <Directory "/usr/lib/cgi-bin">
            AllowOverride None
            Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
            Order allow,deny
            Allow from all
        </Directory>

        WSGIScriptAlias /inkscopeCtrl /var/www/inkscope/inkscopeCtrl/inkscopeCtrl.wsgi
        <Directory "/var/www/inkscope/inkScopeCtrl">
        #<Directory "/var/www/inkscope">
            Order allow,deny
            Allow from all
        </Directory>

        ErrorLog /var/log/apache2/error_inkscope.log

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel warn

        ProxyRequests Off  # we don't want a "forward proxy", but only a "Reverse proxy"
        #ProxyPass /ceph-rest-api/ http://20.20.20.20:5000/api/v0.1/
        ProxyPass /ceph-rest-api/ http://192.168.159.155:5050/api/v0.1/
        ProxyPass /mongodb_status/ http://10.10.10.10:28017
        #ProxyPass /shell http://$IP:4200/

        CustomLog /var/log/apache2/access.log combined
    </VirtualHost>

运行下面的命令，启用apache2的proxy模块和inkScope.conf虚拟主机

::

    sudo a2enmod proxy_http
    sudo a2ensite inkScope.conf
    sudo service apache2 restart

现在打开浏览器访问192.168.159.155:8080/应该就可以看到首页，只是暂时没有ceph集群的相关数据而已。

无法显示页面
++++++++++++++

配置上面的过程之后，正常来说，应该是可以看到页面的。当初因为自己的apache2服务器配置原因，
导致一直出现 ``You don't have permission to access / on this server ubuntu 14.04`` , 另外，
服务器日志总是提示如下错误：

::

    AH01276: Cannot serve directory /var/www/: No matching DirectoryIndex
    (index.html,index.cgi,index.pl,index.php,index.xhtml,index.htm) found,
    and server-generated     directory index forbidden by Options directive

这个问题其实是由于在apache.conf配置文件中没有开启virtual host configuration引起的。

::

    vim /etc/apache2/apache2.conf
    # 开启virtual host配置。
    Include sites-enabled/

    # 然后重启apache2服务
    service apache2 reload
    service apache2 restart

开启 ``Include sites-enabled/`` 配置之前， ``apache2ctl -S`` 命令只能看到监听的80和443端口，
inkscope的8080端口一直无法看到。开启该选项后，就可以正常看到了。

.. figure:: /_static/images/apache2ctl_virtualhost.png
   :scale: 100
   :align: center

   查看apache2的virtual host

开启mongodb远程连接
=====================

修改/etc/mongodb.conf，将bind_ip修改为0.0.0.0，取消port = 27017 依据前面的注释，如下：

::

    bind_ip = 0.0.0.0
    port = 27017


安装cephprobe
==============

在cephprobe节点主要是提供ceph-rest-api并抓取ceph的信息存入mongodb中。所需软件包及依赖安装如下：

::

    apt-get install python-dev
    pip install pymongo psutil
    dpkg -i inkscope-common_1.2.0-0.deb inkscope-sysprobe_1.2.0-0.deb inkscope-cephrestapi_1.2.0-0.deb inkscope-cephprobe_1.2.0-0.deb

启动ceph-rest-api服务： /etc/init.d/ceph-rest-api start

.. important::

    由于在openstack allinone环境部署inkscope，ceph-rest-api监听的是5000端口，
    和openstack keystone所监听的端口冲突，我们可以修改ceph-rest-api源码，
    把DEFAULT_PORT修改为5050。然后重启ceph-rest-api服务！

    ::

        vim /usr/lib/python2.7/dist-packages/ceph_rest_api.py
        # 修改DEFAULT_PORT = '5050'

radosgw服务配置
==================

在ceph1提供radosgw服务，具体radosgw的安装在这里不做详述，请参见ceph官方文档或者内部手册。
这里需要新建一个管理用户，并赋予相关权限，以便在界面上直接操作radosgw。

::

    radosgw-admin user create --uid=inkscope --display-name="Inkscope admin" \
                          --access-key=accesskey --secret=secretkey \
                          --caps="users=*;metadata=*;buckets=*"

这里sccess和secret的具体的值可以根据喜好自行修改。

安装sysprobe
=============

在其他没有承担特殊任务的节点上安装sysprobe

::

    apt-get install python-dev
    pip install pymongo psutil
    dpkg -i inkscope-common_1.2.0-0.deb inkscope-sysprobe_1.2.0-0.deb


inkscope的配置文件就一个，位于/opt/inkscope/etc/inkscope.conf，
最终版如下，需要修改的地方已经单独标出：

.. code-block:: python

    {
        "ceph_conf": "/etc/ceph/ceph.conf",
        # 这里
        "ceph_rest_api": "192.168.159.155:8080",
        "ceph_rest_api_subfolder": "",
        # 这里
        "mongodb_host" : "10.10.10.10",
        "mongodb_set" : "mongodb0:27017,mongodb1:27017,mongodb2:27017",
        "mongodb_replicaSet" : "replmongo0",
        "mongodb_read_preference" : "ReadPreference.SECONDARY_PREFERRED",
        "mongodb_port" : 27017,
        "mongodb_user":"ceph",
        "mongodb_passwd":"monpassword",
        "is_mongo_authenticate" : 0,
        "is_mongo_replicat" : 0,
        "cluster": "ceph",
        "status_refresh": 3,
        "osd_dump_refresh": 3,
        "pg_dump_refresh": 60,
        "crushmap_refresh": 60,
        "df_refresh": 60,
        "cluster_window": 1200,
        "osd_window": 1200,
        "pool_window": 1200,
        "mem_refresh": 60,
        "swap_refresh": 600,
        "disk_refresh": 60,
        "partition_refresh": 60,
        "cpu_refresh": 30,
        "net_refresh": 30,
        "mem_window": 1200,
        "swap_window": 3600,
        "disk_window": 1200,
        "partition_window": 1200,
        "cpu_window": 1200,
        "net_window": 1200,
        # 这里
        "radosgw_url": "http://127.0.0.1:80",
        "radosgw_admin": "admin",
        # 这里
        "radosgw_key": "accesskey",
        # 这里
        "radosgw_secret": "secretkey"
    }


将该文件拷贝到所有节点的/opt/inkscope/etc/ 目录中，然后重启对应服务：

::

    /etc/init.d/sysprobe start
    /etc/init.d/cephprobe start
    /etc/init.d/ceph-rest-api start

对应节点上启动对用服务。此时，应该就可以在页面上看到实时的ceph状态了！


.. figure:: /_static/images/install_inkscope_success.png
   :scale: 100
   :align: center

   安装成功

简单原理分析
=============

简单浏览了下inkscope的代码架构和抓包分析，inkscope是一个基于apache2部署的flask应用。
实际上，该flask项目只负责ceph监控页面展示，而实际获取ceph集群状态信息，是通过向ceph-rest-api发起请求实现的。

然后在页面上对应的js代码中，通过不断的发起ajax请求，获取ceph json状态数据，来更新整个前端显示信息。
如图所示抓包信息，页面不断发起请求更新ceph显示状态。

.. figure:: /_static/images/ceph_rest_api_status_json.png
   :scale: 100
   :align: center

   页面不断发起ajax请求更新状态

然后在inkscope.conf中，有一条代理设置 ``ProxyPass /ceph-rest-api/ http://192.168.159.155:5050/api/v0.1/`` ，
所以所有以/ceph-rest-api开始的url最后都向http://192.168.159.155:5050/api/v0.1/发起请求，正是ceph-rest-api服务，
然后返回json格式数据。

抽时间，分析下inkscope项目的源码，也好学习下flask框架！

.. [#] 跟着该博文操作，基本不会出现什么问题。http://cloud.51cto.com/art/201507/486005.htm
