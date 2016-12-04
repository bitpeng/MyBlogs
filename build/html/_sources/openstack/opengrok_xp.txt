.. _opengrok_xp:


########################
OpenGrok代码浏览环境搭建
########################


..
    标题 ####################
    一号 ====================
    二号 ++++++++++++++++++++
    三号 --------------------
    四号 ^^^^^^^^^^^^^^^^^^^^


最近在分析nova-api 服务启动流程，为了能方便的浏览Python代码，尝试过了很多工具。
比如：Pycharm, Sublime Text, Notepad++, Source Insight + Python.CLF, 结果发现
这样那样的问题。最后在知乎上经过 韦一笑的推荐，尝试 OpenGrok, 今天体验了一番，
感觉不错。于是记录下来！


.. contents:: 目录

--------------------------

tomcat 安装
============

由于公司的云环境已经安装了tomcat 服务器，因此这一步可以直接略过！

OpenGrok 部署
=============

以下部署OpenGrok过程:

::

    cd /smbshare
    # 下载opengrok
    wget https://github.com/OpenGrok/OpenGrok/files/213268/opengrok-0.12.1.5.tar.gz
    tar -xvzf opengrok-0.12.1.5.tar.gz
    # 拷贝web app源文件
    cp opengrok-0.12.1.5/lib/source.war /opt/apache-tomcat-7.0.50/webapps/
    # 安装CTags
    dpkg -i exuberant-ctags_1%3a5.9~svn20110310-7ubuntu0.1_amd64.deb
    # 或者apt-get install ctags
    # 生成代码索引
    cd opengrok-0.12.1.5/bin
    ./OpenGrok index /opt/cecgw/csmp/nova

    # 重新生成新代码索引
    # 删除原索引，然后再生成！
    rm -rf /var/opengrok
    ./OpenGrok index /opt/cecgw/csmp/nova

生成代码索引后，就可以打开网页，进行代码浏览了。

.. figure:: /_static/images/opengrok_access.png
   :scale: 100
   :align: center

   打开网址浏览代码


