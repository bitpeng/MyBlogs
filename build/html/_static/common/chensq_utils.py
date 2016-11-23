#coding:utf-8

def get_logger():
    import logging
    # 创建一个logger
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)

    # 创建一个handler，用于写入日志文件 
    fh = logging.FileHandler('/smbshare/openstack.log')
    fh.setLevel(logging.DEBUG)

    # 再创建一个handler，用于输出到控制台 
    #ch = logging.StreamHandler() 
    #ch.setLevel(logging.DEBUG) 

    # 定义handler的输出格式 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    #ch.setFormatter(formatter) 

    # 给logger添加handler 
    logger.addHandler(fh)
    #logger.addHandler(ch) 

    # 记录一条日志 
    #logger.info('foorbar')
    return logger

def log_debug_bad(*a, **ka):
    """
    曾经尝试使用Python的logging模块写一个简单的日志系统；
    但是由于Python logging模块一些易出错的特性，并不好用。
    因此该模块应该标记为过时。
	
	使用另外的模块代替。`log_debug`
    """
    import sys
    import os
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    co_filename = f.f_code.co_filename
    co_filename = os.path.abspath(co_filename)
    #return (__file__, f.f_code.co_filename, f.f_code.co_name, f.f_lineno)
    #print "+++===+++: `%s`,     <+ %s +>,   <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka)
    logger = get_logger()
    logger.info("+++===+++: `%s`,  <+ %s +>,  <=+ %s +=>"%
                 ((co_filename, f.f_code.co_name, f.f_lineno), a, ka))

def print_debug(*a, **ka):
    import sys
    import os
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    co_filename = f.f_code.co_filename
    co_filename = os.path.abspath(co_filename)
    #return (__file__, f.f_code.co_filename, f.f_code.co_name, f.f_lineno)
    if ka:
        print "+++===+++: %s,  <+ %s +>,  <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka)
    else:
        print "+++===+++: %s,  <+ %s +>"%((co_filename, f.f_code.co_name, f.f_lineno), a)

class ChenLog(object):
    def __init__(self, fn):
        self.fn = fn
        self.fp = None

    #def logging(self, text):
    #    self.fp.write(text+'\n')

    #def __call__(self, *a, **ka):
    #    self.fp.write("%s, %s\n"%(a, ka))

    def __call__(self, text):
        self.fp.write("%s\n"%text)

    def __enter__(self):
        #print("__enter__")
        #self.fp=open(self.filename,"a+")
        self.fp=open(self.fn, "a+")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #print("__exit__")
        self.fp.close()

def log_debug(*a, **ka):
    import sys
    import os
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    co_filename = f.f_code.co_filename
    co_filename = os.path.abspath(co_filename)
    #return (__file__, f.f_code.co_filename, f.f_code.co_name, f.f_lineno)
    #print "+++===+++: `%s`,  <+ %s +>,  <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka)

    with ChenLog("/smbshare/test.log") as log:
        #log("+++===+++: %s : <+ %s +> : <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka))
        log("+++===+++: %s ; <+ %s +> ; <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka))
        #print ("+++===+++: %s,  <+ %s +>,  <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka))
        #log("+++===+++: `%s`,  <+ %s +>,  <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka))


if __name__ == "__main__":
    print_debug(1,2,3)
    print_debug(1, 2, 3, a=4, d=5)
    #log_debug("a", 1, 2)
    #log_debug(1, 2, 3, a=4, d=5)
