
tips
########


各种各样的tips和乱七八糟的记录！


--------------------------

- 问：Firefox打开httpfox

  答：使用快捷键：ctrl+shift+F2

--------------------------

- 问：ubuntu apt-get下载的deb包目录

  答：/var/cache/apt/archives

--------------------------

- 问：win10系统VMI provide host进程占用CPU过高

  答：网上找了很多，都是千篇一律的关闭windows firewall，实际上根本没用。
  不断搜索，总算找到一个靠谱的解决方案！

  Windows键 +r 打开“启动”，输入services.msc打开“服务”，找到“Windows Management Instrumentation”，
  右键“重新启动”。 **亲测有效** 。具体可以参考： https://www.zhihu.com/question/48491814

--------------------------

- 问：电脑重启后，vmware启动虚机提示"内部错误"

  答： Windows键 +r 打开“启动”，输入services.msc打开“服务”，然后依次启动vmware相关服务！
  **亲测有效** 。

  另外，网络上说，可以右键vmware，然后选择以管理员身份运行！
