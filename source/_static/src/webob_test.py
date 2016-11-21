#coding:utf-8

import webob
import webob.dec
import webob.exc

'''
我们知道，wsgi规定了web server和web app之间的接口。
但是通过environ 传递http request信息，有点不太直观，并且
使用start_response 回调函数，逻辑也显得比较难以理解。

一般而言，web app的正常调用逻辑是：

res = func(req)

即func接收HTTP req请求，并返回HTTP response。但是func的接口，
并不符合wsgi的规定。因此webob就派上用场了，该库的任务
之一就是把普通的函数(后面的例子可以看到，函数参数和返回类型
有限制)通过装饰器包装，转化成标准的wsgi app。
'''

#==================================================#

"""
webob 测试程序一：
从这里可以看到，我们只要定义函数，接收 `webob.Request`类型的参数，
并返回`webob.Response`类型的对象。我们就可以通过`wsgify`装饰器进行
包装，使之成为标准的wsgi app(接收environ, start_response参数的app)
"""

@webob.dec.wsgify
def myfunc(req):
    print req
    print type(req)
    return webob.Response('hey there\n')
    #return 'hey there\n'
    #return u"1900"

#myfunc = webob.dec.wsgify(myfunc)

#==================================================#

"""
webob 测试程序二：

程序一中req是<class 'webob.request.Request'> 类型的(可以通过
print type查看)。此外，req参数也可以是Request class的子类。

这里，我们自定义MyRequest 继承自Request，然后传给装饰器参数，
因此myfun2 的req类型是MyRequest.
"""

class MyRequest(webob.Request):
    @property
    def is_local(self):
        return self.remote_addr == '127.0.0.1'

@webob.dec.wsgify(RequestClass=MyRequest)
def myfunc2(req):
    print type(req)
    if req.is_local:
        return webob.Response('hi!\n')
    else:
        raise webob.exc.HTTPForbidden

#==================================================#

from wsgiref.simple_server import make_server

#httpd = make_server('127.0.0.1', 9999, myfunc)
#httpd = make_server('127.0.0.1', 9999, myfunc2)
httpd = make_server('0.0.0.0', 9999, myfunc2)
#httpd = make_server('0.0.0.0', 9999, myfunc)
httpd.serve_forever()
