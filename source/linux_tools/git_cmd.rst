git 版本控制
================

提交代码流程
--------------------

.. code:: shell

    git init
    git add <file/dir>
    git commit -m "info"
    git remote add origin https://github.com/bitpeng/MyBlogs.git
    git push -u origin master
    git status

    # 查看提交历史记录
    git log
    # 查看最近n次提交历史记录
    git log -n

    # 查看某次提交修改内容
    git show <id>
    git show <id> file

    # 查看文件提交记录
    git log file
    # 查看文件提交每次修改信息
    git log -p file
