#coding: utf-8

'''''
Created on 2011-6-12
@author: Sonic
'''

import os
import webob
from webob import Request
from webob import Response
from paste.deploy import loadapp
from wsgiref.simple_server import make_server
from time import sleep

#Filter

class TestFilter():
    def __init__(self,app):
        print "call test_filter init\n"
        self.app = app

    def __call__(self,environ,start_response):
        print "filter: call Test_Filter."
        return self.app(environ,start_response)

    @classmethod
    def factory(cls, global_conf, **kwargs):
        print "in Test_Filter.factory", global_conf, kwargs
        return TestFilter

class LogFilter():
    def __init__(self,app):
        print "call log filter init\n"
        self.app = app

    def __call__(self,environ,start_response):
        print "filter:LogFilter is called."
        return self.app(environ,start_response)

    @classmethod
    def factory(cls, global_conf, **kwargs):
        print "in LogFilter.factory", global_conf, kwargs
        return LogFilter

class ShowVersion():
    def __init__(self):
        print "call showversion init\n"

    def __call__(self,environ,start_response):
        print "showversion call"
        start_response("200 OK",[("Content-type", "text/plain")])
        return ["Paste Deploy LAB: Version = 1.0.0\n",]

    @classmethod
    def factory(cls,global_conf,**kwargs):
        print "in ShowVersion.factory", global_conf, kwargs
        return ShowVersion()



class Calculator():
    def __init__(self):
        print "call calc init\n"

    def __call__(self,environ, start_response):
        #print environ
        print "calculator call"
        req = Request(environ)
        res = Response()
        res.status = "200 OK"
        res.content_type = "text/plain"
        # get operands
        operator = req.GET.get("oper", None)
        operand1 = req.GET.get("op1", None)
        operand2 = req.GET.get("op2", None)
        print req.GET
        #print operand1, operand2
        #sleep(10)
        opnd1 = int(operand1)
        opnd2 = int(operand2)
        if operator == u'plus':
            opnd1 = opnd1 + opnd2
        elif operator == u'minus':
            opnd1 = opnd1 - opnd2
        elif operator == u'star':
            opnd1 = opnd1 * opnd2
        elif operator == u'slash':
            opnd1 = opnd1 / opnd2
        res.body = "%s \nRESULT = %d\n" % (str(req.GET) , opnd1)
        #return [res.body]
        return res(environ,start_response)
        #start_response("200 OK",[("Content-type", "text/plain")])
        #return ["call calc\n"]

    @classmethod
    def factory(cls,global_conf,**kwargs):
        print "in Calculator.factory", global_conf, kwargs
        return Calculator()

if __name__ == '__main__':
    configfile="pastedeploylab.ini"
    appname="pdl"
    #wsgi_app = loadapp("config:%s" % os.path.abspath(configfile), appname)
    wsgi_app = loadapp("config:%s" % os.path.abspath(configfile), "test_paste")
    server = make_server('localhost', 9999, wsgi_app)
    server.serve_forever()
    pass
