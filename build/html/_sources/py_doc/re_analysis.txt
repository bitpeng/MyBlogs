Python正则表达式分析利器
========================

tags： Python 正则表达式

.. note::
    在学习正则表达式及Python
    re模块中，发现一个分析正则模式的利器，下面根据自己在阅读代码时见到的最复杂的正则表达式，来进行分析。

.. code:: Python

    import re
    # 该正则表达式来源于bottle框架的URL正则匹配模式，非常复杂！
    re.compile('(\\\\*)'\
            '(?:(?::([a-zA-Z_][a-zA-Z_0-9]*)?()(?:#(.*?)#)?)'\
              '|(?:<([a-zA-Z_][a-zA-Z_0-9]*)?(?::([a-zA-Z_]*)'\
                '(?::((?:\\\\.|[^\\\\>]+)+)?)?)?>))', re.DEBUG)


    # 以下为在命令行交互模式下的输出！逐行进行分析。
    subpattern 1  # 捕获分组，编号为1.
      max_repeat 0 4294967295   # 贪婪匹配
        literal 92              # 匹配反斜杠
    subpattern None             # 非捕获分组
      branch                    # 选择结构
        subpattern None         # 非捕获分组
          literal 58            # 匹配:
          max_repeat 0 1        # 可选的?
            subpattern 2        # 捕获分组，编号为2.
              in                # 字符类 []
                range (97, 122)   # a-z
                range (65, 90)     # A-Z
                literal 95         # 匹配_
              max_repeat 0 4294967295    # 贪婪匹配
                in                       # 字符类
                  range (97, 122)        # 后面的依次进行分析即可。
                  range (65, 90)
                  literal 95
                  range (48, 57)
          subpattern 3
          max_repeat 0 1
            subpattern None
              literal 35
              subpattern 4
                min_repeat 0 4294967295
                  any None
              literal 35
      or
        subpattern None
          literal 60
          max_repeat 0 1
            subpattern 5
              in
                range (97, 122)
                range (65, 90)
                literal 95
              max_repeat 0 4294967295
                in
                  range (97, 122)
                  range (65, 90)
                  literal 95
                  range (48, 57)
          max_repeat 0 1
            subpattern None
              literal 58
              subpattern 6
                max_repeat 0 4294967295
                  in
                    range (97, 122)
                    range (65, 90)
                    literal 95
              max_repeat 0 1
                subpattern None
                  literal 58
                  max_repeat 0 1
                    subpattern 7
                      max_repeat 1 4294967295
                        subpattern None
                          branch
                            literal 92
                            any None
                          or
                            max_repeat 1 4294967295
                              in
                                negate None      # 匹配除去字符类中的其他字符，^
                                literal 92
                                literal 62
          literal 62
    <_sre.SRE_Pattern object at 0x1381f70>

