Samba共享访问配置
====================


.. note::
    有时需要在在Windows和Linux之间传输文件，可以通过Samba共享实现。实例尝试
    在windows下访问Linux中文件，通过在Linux配置samba,smb用户名为smbuser1:123456.共享访问目录为/smbshare

自动化脚本
--------------------


.. literalinclude:: src-samba_share.sh
   :language: bash
   :emphasize-lines: 12,15-18
   :linenos:
