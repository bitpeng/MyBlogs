.. _unittest:


########################
unittest单元测试
########################


.. contents:: 目录

--------------------------

最近花时间研究了下python的单元测试框架unittest，
在简要熟悉了该框架的用法之后，简要分析了下该框架的源码，
现在从源代码的角度，来对xUnit单元测试的一些基本概念和核心原理进行讲解。

先给出简单的用法示例：

::

    import unittest
    import clog

    class Mydemo(unittest.TestCase):
        def setUp(self):
            print '<+' * 10
            print "in test setUp"
            self.a=1

        def tearDown(self):
            print "tear down"
            #self.a=1
            print '+>' * 10
            print

        def test1(self):
            print "i am test1 the value of a is {}".format(self.a)

        def test2(self):
            print "i am test2 the value of a is {}".format(self.a)

        def  test3(self):
            print "i am test3 the value of a is {}".format(self.a)

    class TestStringMethods(unittest.TestCase):
        def setUp(self):
            print '<+' * 10 , "in test setUp"
            self.a=1
            clog.LOG_STACK()

        def tearDown(self):
            print "tear down", '+>' * 10
            print
            clog.LOG_STACK()

        @classmethod
        def setUpClass(cls):
            print "++" * 5 + "setupclass" + "++" * 5
            clog.LOG_STACK()

        @classmethod
        def tearDownClass(cls):
            print "==" * 5 + "tearDownClass" + "==" * 5
            clog.LOG_STACK()

        def test_upper(self):
            print "test_upper"
            self.assertEqual('foo'.upper(), 'FOO')
            self.assertEqual('foo'.upper(), 'FOO9')

        def test_isupper(self):
            print "test_isupper"
            self.assertTrue('FOO'.isupper())
            self.assertFalse('Foo'.isupper())

        def test_split(self):
            print "test_issplit"
            self.assertTrue('FOO'.isupper())
            s = 'hello world'
            self.assertEqual(s.split(), ['hello', 'world'])
            # check that s.split fails when the separator is not a string
            with self.assertRaises(TypeError):
                s.split(2)

    def setUpModule():
        print "<start>" * 3
        clog.LOG_STACK()

    def tearDownModule():
        print "<end>" * 5
        clog.LOG_STACK()

    if __name__ == '__main__':
        unittest.main()


大家自行运行上面的例子，后面会结合相关的概念，从源代码角度对运行结果进行分析。

基本概念
=========

.. attribute:: TestCase

    一个testcase是测试中最小的一个单元，它用于检查特定的一组输入或响应，
    unittest中提供了一个TestCase类，可以用来创建新的测试用例。

    **需要注意一点，每一个继承自TestCase类，并且以test开头的方法，都是一个测试用例。
    如TestStringMethods类有三个以test开头的方法，那么会根据这三个方法，
    生成三个TestCase实例(然后根据这三个testcase实例，生成一个testsuite)。**

.. attribute:: TestSuite

    可迭代对象，他的每一个元素是TestCase实例或者是其他TestSuite实例。

    比如上面的例子，Mydemo和TestStringMethods会各生成一个TestSuite实例，
    最后根据这两个suite实例生成一个suite实例。

    **testsuite实例是可迭代的，testcase不可迭代。**

.. attribute:: TestLoader

    用来加载TestCase到TestSuite中，
    其中的方法从各个地方寻找TestCase，创建它们的实例，
    然后add到TestSuite中，返回一个TestSuite实例。

.. attribute:: TestRunner

    驱动执行测试，并输出测试结果呈现给用户。

    TestRunner有一个关键的stream参数，表示要将测试的结果，格式化输出到什么地方(默认是sys.stderr)。

.. attribute:: TestResult

    保存测试结果。包括运行用例数，成功数，失败数等。

    关于测试结果，我们需要注意测试错误和测试失败的区别。来看官网的描述：

    `If the test fails, an exception will be raised, and unittest will identify the test case as a failure. Any other exceptions will be treated as errors. This helps you identify where the problem is: failures are caused by incorrect results - a 5 where you expected a 6. Errors are caused by incorrect code - e.g., a TypeError caused by an incorrect function call.`

    简而言之，测试失败表示对于要测试的函数，没有得到预期的结果。
    而测试错误，表示测试代码本身有问题。

.. attribute:: test-fixture

    测试固件，不同于以上概念在unittest框架源代码中都有对应的实体(如有TestCase类、TestSuite类)，
    在unittest源码中并没有直接体现出test-fixture。可以认为这是一个逻辑上的概念，
    表示每运行一个测试用例时，事先的准备工作(如打开文件、连接数据)、
    执行测试本身和测试完毕的清理工作等整个流程。

    对应在源码级别，可以通过setUpModule/setUpClass/setUp等方式，对测试流程进行精细控制。


核心实现
=========

test加载
+++++++++

以我们上面的测试代码为例，从module中加载tests，通过loadTestsFromModule方法实现。

::

    # 对每一个TestCase派生类，生成一个TestSuite实例，
    # TestSuite实例保存着以test开头的方法。
    def loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all tests cases contained in testCaseClass"""
        if issubclass(testCaseClass, suite.TestSuite):
            raise TypeError("Test cases should not be derived from TestSuite." \
                                " Maybe you meant to derive from TestCase?")
        testCaseNames = self.getTestCaseNames(testCaseClass)
        if not testCaseNames and hasattr(testCaseClass, 'runTest'):
            testCaseNames = ['runTest']
        tmp = map(testCaseClass, testCaseNames)
        loaded_suite = self.suiteClass(tmp)
        return loaded_suite

    # 从模块中加载tests，返回的结果是TestSuite实例。
    def loadTestsFromModule(self, module, use_load_tests=True):
        """Return a suite of all tests cases contained in the given module"""
        tests = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, case.TestCase):
                tests.append(self.loadTestsFromTestCase(obj))

        # 从这里可以看到，我们可以针对模块自定义test加载方法。
        # 在模块中定义一个load_tests函数即可。
        load_tests = getattr(module, 'load_tests', None)
        tests = self.suiteClass(tests)
        if use_load_tests and load_tests is not None:
            try:
                return load_tests(self, tests, None)
            except Exception, e:
                return _make_failed_load_tests(module.__name__, e,
                                               self.suiteClass)
        return tests

    # 从TestCase类中查找所有的以test开头的函数。
    # 返回列表。
    def getTestCaseNames(self, testCaseClass):
        """Return a sorted sequence of method names found within testCaseClass
        """
        def isTestMethod(attrname, testCaseClass=testCaseClass,
                         prefix=self.testMethodPrefix):
            return attrname.startswith(prefix) and \
                hasattr(getattr(testCaseClass, attrname), '__call__')
        testFnNames = filter(isTestMethod, dir(testCaseClass))
        if self.sortTestMethodsUsing:
            testFnNames.sort(key=_CmpToKey(self.sortTestMethodsUsing))
        return testFnNames

test-fixture
+++++++++++++

测试固件那一套复杂的控制逻辑，主要是通过TestResult来实现的。

还是以上面的测试代码为例进行说明：

- setUp/tearDown对每个TestCase都会执行(每个test都是一个Testcase)。
- setUpClass/tearDownClass，对每个TestCase-subclass执行一次。(如果setUpClass发生异常，
则该class中的test都不会执行，tearDownClass也不会被执行)
- setUpModule/tearDownModule，对每个模块执行一次。(如果setUpModule执行发生异常，
那么该模块中所有的test和tearDownModule都不会被执行)


**注意，TestResult类是用来简单保存测试结果的。至于测试结果的格式化输出，则不是这个类的任务。
unittest中有一个TextTestResult类，可以对测试输出结果信息进行控制显示(如使用-v参数)**。
当然，我们可以通过继承TestResult来，来定制自己的test-result。

在整个测试过程中，有且仅有一个test-result对象。所有的test执行过程中，
都会以test-result对象作为参数，原地记录并更改测试结果信息。

其次，在测试过程中，利用TestResult的三个关键类属性，对控制逻辑实现精确控制。

::

    class TestResult(object):
        _previousTestClass = None
        _testRunEntered = False
        _moduleSetUpFailed = False

    ......

    def run(self, result, debug=False):
        topLevel = False
        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True

        for test in self:
            if result.shouldStop:
                break

            if _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__

                if (getattr(test.__class__, '_classSetupFailed', False) or
                    getattr(result, '_moduleSetUpFailed', False)):
                    continue

            if not debug:
                test(result)
            else:
                test.debug()

        if topLevel:
            self._tearDownPreviousClass(None, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = False
        return result

通过_testRunEntered属性，标记测试开始，通过配合toplevel参数，实现setUpModule/ tearDownModule逻辑。

其次，在每执行一个test过程中，会对比当前test所属的TestCaseClass和_previousTestClass：

::

    def _handleClassSetUp(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        if result._moduleSetUpFailed:
            return
        if getattr(currentClass, "__unittest_skip__", False):
            return

        try:
            currentClass._classSetupFailed = False
        except TypeError:
            # test may actually be a function
            # so its class will be a builtin-type
            pass

        setUpClass = getattr(currentClass, 'setUpClass', None)
        if setUpClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                setUpClass()
            except Exception as e:
                if isinstance(result, _DebugResult):
                    raise
                currentClass._classSetupFailed = True
                className = util.strclass(currentClass)
                errorName = 'setUpClass (%s)' % className
                self._addClassOrModuleLevelException(result, e, errorName)
            finally:
                _call_if_exists(result, '_restoreStdout')
                
            
如果两者相同，则不用执行setUpClass方法，否则表示是其他TestCase-subclass所属的test，
那么需要执行setUpClass方法，并更新_previousTestClass。通过该属性，
能保证setUpClas/ tearDownClass对每个类只会执行一次。

对代码进行讲解，是一件很费力的事情。请大家参考unittest代码，进行分析。

参考
=====

.. [#] https://huilansame.github.io/huilansame.github.io/archivers/python-unittest#进阶用htmltestrunner输出漂亮的html报告
.. [#] http://lucia.xicp.cn/2016/05/16/python/python%E5%8D%95%E5%85%83%E6%B5%8B%E8%AF%95unittest/

