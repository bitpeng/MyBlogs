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
    print "+++===+++: `%s`,  <+ %s +>,  <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka)

if __name__ == "__main__":
    print_debug(1,2,3)
    log_debug("a", 1, 2)
