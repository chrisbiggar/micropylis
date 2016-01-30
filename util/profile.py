'''
profile module.
Contains all the profiling resources for micropylis.

'''
import time








def timefunc(f):
    '''
    Use as decorator to time a function.
    Low resolution. Not for quick functions.
    '''
    def f_timer(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print f.__name__, 'took', end - start, 'time'
        return result
    return f_timer