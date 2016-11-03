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
    print "+++===+++: `%s`,     <+ %s +>,   <=+ %s +=>"%((co_filename, f.f_code.co_name, f.f_lineno), a, ka)