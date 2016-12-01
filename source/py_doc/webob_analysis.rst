.. _webob_analysis:


webob库简单分析
###############

首先来看一个例子。

.. code-block:: python
    :linenos:

    #coding:utf-8
    from webob import Request
    from webob import Response
    import webob.dec

    """
    经测试，使用wsgify包装的wsgi app, 可以返回另一个wsgi app，
    然后req请求交给返回的app处理！返回的wsgi app可以是通过原
    始的方式定义的(接收env, start_response参数)。也可以是使用
    wsgify包装的！

    如该例子中，test_app 通过wsgify包装，成为一个wsgi app，然后他
    返回另一个wsgi app：simple_app_2，webob库保证接下来会调用
    simple_app_2，并把它返回的结果发送给web server！这样的好处
    是对于一个请求，能通过链式的方式一次让每一个app依次处理。

    这种链式处理的方式，在OpenStack REST-API中使用得非常频繁。

    通过(env, start_response)参数定义的wsgi app不具备该功能。
    """

    @webob.dec.wsgify
    def test_app(req):
        print "call test_app"
        print "----:%s"%simple_app_2
        return simple_app_2
        # 返回simple_app也是可以的。webob会把simple_app的结果发送给web_server!
        #return simple_app

    #test_app = wsgify(test_app)
    #test_app(evn, start_response)

    @webob.dec.wsgify
    def simple_app_2(req):
        print "call app2"
        return webob.Response("hello, app2!\n")

    #simple_app_2 = wsgify(simple_app_2)

    # 通过标准方式定义的wsgi app
    def simple_app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type','text/plain')]
        start_response(status, response_headers)
        return ['Hello world!\n', "return test\n"]

    httpd = make_server('0.0.0.0', 9999, test_app)
    httpd.serve_forever()


利用wsgiref作为web server, test_app 作为wsgi app启动服务。
服务器会收到请求后，会调用test_app.

::

    res = test_app(evn, start_response)

test_app实际上此时是一个wsgify对象，因此会执行wsgify.__call__函数，现在来分析
该核心函数！


wsgify核心代码分析：

.. code-block:: python
    :linenos:

    class wsgify(object):
        """Turns a request-taking, response-returning function into a WSGI
        app
        You can use this like::
            @wsgify
            def myfunc(req):
                return webob.Response('hey there')
        With that ``myfunc`` will be a WSGI application, callable like
        ``app_iter = myfunc(environ, start_response)``.  You can also call
        it like normal, e.g., ``resp = myfunc(req)``.  (You can also wrap
        methods, like ``def myfunc(self, req)``.)
        If you raise exceptions from :mod:`webob.exc` they will be turned
        into WSGI responses.
        There are also several parameters you can use to customize the
        decorator.  Most notably, you can use a :class:`webob.Request`
        subclass, like::
            class MyRequest(webob.Request):
                @property
                def is_local(self):
                    return self.remote_addr == '127.0.0.1'
            @wsgify(RequestClass=MyRequest)
            def myfunc(req):
                if req.is_local:
                    return Response('hi!')
                else:
                    raise webob.exc.HTTPForbidden
        Another customization you can add is to add `args` (positional
        arguments) or `kwargs` (of course, keyword arguments).  While
        generally not that useful, you can use this to create multiple
        WSGI apps from one function, like::
            import simplejson
            def serve_json(req, json_obj):
                return Response(json.dumps(json_obj),
                                content_type='application/json')
            serve_ob1 = wsgify(serve_json, args=(ob1,))
            serve_ob2 = wsgify(serve_json, args=(ob2,))
        You can return several things from a function:
        * A :class:`webob.Response` object (or subclass)
        * *Any* WSGI application
        * None, and then ``req.response`` will be used (a pre-instantiated
          Response object)
        * A string, which will be written to ``req.response`` and then that
          response will be used.
        * Raise an exception from :mod:`webob.exc`
        Also see :func:`wsgify.middleware` for a way to make middleware.
        You can also subclass this decorator; the most useful things to do
        in a subclass would be to change `RequestClass` or override
        `call_func` (e.g., to add ``req.urlvars`` as keyword arguments to
        the function).
        """

        RequestClass = Request

        def __init__(self, func=None, RequestClass=None,
                     args=(), kwargs=None, middleware_wraps=None):
            # self.func 赋值为 test_app
            self.func = func
            if (RequestClass is not None
                and RequestClass is not self.RequestClass):
                self.RequestClass = RequestClass
            self.args = tuple(args)
            if kwargs is None:
                kwargs = {}
            self.kwargs = kwargs
            self.middleware_wraps = middleware_wraps

        def __repr__(self):
            return '<%s at %s wrapping %r>' % (self.__class__.__name__,
                                               id(self), self.func)

        def __get__(self, obj, type=None):
            # This handles wrapping methods
            if hasattr(self.func, '__get__'):
                return self.clone(self.func.__get__(obj, type))
            else:
                return self

        def __call__(self, req, *args, **kw):
            """Call this as a WSGI application or with a request"""
            # test_app(evn, start_response)
            # 因此req = env, args = (start_response, ), kw = {}
            func = self.func
            if func is None:
                if args or kw:
                    raise TypeError(
                        "Unbound %s can only be called with the function it "
                        "will wrap" % self.__class__.__name__)
                func = req
                return self.clone(func)
            if isinstance(req, dict):
                if len(args) != 1 or kw:
                    raise TypeError(
                        "Calling %r as a WSGI app with the wrong signature" %
                        self.func)
                environ = req
                start_response = args[0]
                # 根据env 生产req 对象
                req = self.RequestClass(environ)
                req.response = req.ResponseClass()
                try:
                    args = self.args
                    if self.middleware_wraps:
                        args = (self.middleware_wraps,) + args
                    # 调用实际的包装函数，这里为test_app
                    # test_app(req, *(), **{})
                    # 返回simple_app_2, resp 为simple_app_2
                    resp = self.call_func(req, *args, **self.kwargs)
                except HTTPException as exc:
                    resp = exc
                if resp is None:
                    ## FIXME: I'm not sure what this should be?
                    resp = req.response
                if isinstance(resp, text_type):
                    resp = bytes_(resp, req.charset)
                if isinstance(resp, bytes):
                    body = resp
                    resp = req.response
                    resp.write(body)
                if resp is not req.response:
                    resp = req.response.merge_cookies(resp)
                # 调用simple_app_2(environ, start_response)；
                # simple_app_2也是一个wsgify 对象，从而引起simple_app_2.__call__函数调用。
                # 从而实现链式处理！
                return resp(environ, start_response)
            else:
                if self.middleware_wraps:
                    args = (self.middleware_wraps,) + args
                return self.func(req, *args, **kw)


web server将http请求转发给test_app(evn, start_response),
会引起test_app.__call__函数调用。

- 82行：记录包装的函数；
- 90行：初次请求，req 实际上env, 是一个dict；
- 96行：获取web server 提供的start_response 参数；
- 107行：调用包装的函数，就是原始的test_app，执行完成后，resp = simple_app_2;
- 124行：继续调用simple_app_2 对象！又会引起下一轮simple_app_2.__call__调用。

在simple_app_2.__call__调用中：
在107行处获取最终的结果：webob.Response 对象。
最后还是会执行第24行，Response class定义了__call__函数！
待后面分析。


