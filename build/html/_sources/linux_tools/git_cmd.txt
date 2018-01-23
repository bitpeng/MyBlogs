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
    git show <id> <file>

    # 查看文件提交记录
    git log <file>
    # 查看文件提交每次修改信息
    git log -p <file>


分布管理
--------


.. code:: shell

    # 查看分支
    git branch
    git branch -r
    git branch -a
    # 基于远程分支创建本地分支
    git checkout origin/day-05 -b myday-05
    git checkout origin/day-05 -b day-05
    # 合并分支
    git merge myday-05
    # 推送本地分支到远程分支
    git push origin day-05
    git push origin myday-05
    # 删除本地分支
    git branch -d myday-05
    # 删除远程分支
    git push origin --delete myday-05

Git命令图表

.. figure:: /_static/images/git-cmd.jpg
   :scale: 100
   :align: center

   git命令图表
