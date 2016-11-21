#coding:utf-8

from __future__ import print_function
from routes import Mapper
import webob.dec
import webob.exc
import routes.middleware
import testtools

'''
该程序如如下目的：

1. 测试OpenStack rest服务的处理逻辑，顺序为:

   Python Delopy -- > MyRouter --> routes.middleware.RoutesMiddleware 
   --> MyApplication --> MyController

2. 测试wsgi app返回Unicode字符串问题。curl请求会报错！
   所以需要判断，假如是Unicode对象，需要手动转换成str

'''

class MyController(object):
    def getlist(self, mykey):
        print("step 4: MyController's getlist(self, mykey) is invoked")
        #return "getlist(), mykey=" + mykey
        print ('mykey:%s'%type(mykey))
        ret = "getlist(), mykey=%s\n"%mykey
        print ('ret:%s'%type(ret))
        return ret

class MyApplication(object):
    """Test application to call from router."""

    def __init__(self, controller):
        self._controller = controller

    def __call__(self, environ, start_response):
        print("step 3: MyApplication is invoked")

        action_args = environ['wsgiorg.routing_args'][1].copy()
        try:
            del action_args['controller']
        except KeyError:
            pass

        try:
            del action_args['format']
        except KeyError:
            pass

        action = action_args.pop('action', None)
        controller_method = getattr(self._controller, action)
        result = controller_method(**action_args)

        start_response('200 OK', [('Content-Type', 'text/plain')])
        # wsgi app 不能返回Unicode对象！所以需要转换成字节串.
        if type(result) == type(u'o'):
            result = str(result)
        return [result]

        # 不能用改行，否则会提示Response 对象不可以迭代错误！
        #return webob.Response(result)

class MyRouter(object):
    """Test router."""

    def __init__(self):
        route_name = "dummy_route"
        route_path = "/dum"

        my_application = MyApplication(MyController())
        #my_application = MyApp2(MyController())

        self.mapper = Mapper()
        self.mapper.connect(route_name, route_path,
                        controller=my_application,
                        #action="getlist-2",
                        action="getlist",
                        mykey="myvalue",
                        conditions={"method": ['GET']})

        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          self.mapper)

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        """Route the incoming request to a controller based on self.map.

        If no match, return a 404.

        """
        print("step 1: MyRouter is invoked")
        return self._router

    @staticmethod
    @webob.dec.wsgify(RequestClass=webob.Request)
    def _dispatch(req):
        """Dispatch the request to the appropriate controller.

        Called by self._router after matching the incoming request to a route
        and putting the information into req.environ.  Either returns 404
        or the routed WSGI app's response.

        """
        print("step 2: RoutesMiddleware is invoked, calling our _dispatch back")

        match_dict = req.environ['wsgiorg.routing_args'][1]
        if not match_dict:
            return webob.exc.HTTPNotFound()
        app = match_dict['controller']
        return app

from wsgiref.simple_server import make_server

httpd = make_server('0.0.0.0', 9999, MyRouter())
httpd.serve_forever()
