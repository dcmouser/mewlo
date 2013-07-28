# callables.py
"""Support functions to help find dynamic callables"""


def find_callable_from_dottedpath(callablepath):
    # given a dotted path, find the callable
    # see http://stackoverflow.com/questions/6643324/how-is-calling-module-and-function-by-string-handled-in-python
    # return tuple (funcreferce, errorstr)

    # get splitted name
    modulepath, functionname = callablepath_dotsplit(callablepath)

    try:
        #print "ATTN: trying to import modulepath: '"+modulepath+"' and functionname: '"+functionname+"'\n"
        mod = __import__(modulepath, globals(), locals(), [functionname,], -1)
    except Exception:
        return (None, "From '"+callablepath+"', failed to module import '"+modulepath+"': "+str(Exception))
    #
    try:
        func = getattr(mod,functionname)
    except Exception:
        return (None, "From '"+callablepath+"', imported module '"+modulepath+"' but failed to find function '"+functionname+"': "+str(Exception))
    #
    return (func, "")


def callablepath_dotsplit(dottedname):
    from string import join
    #
    modulepath = join(dottedname.split('.')[:-1],'.')
    functionname = dottedname.split('.')[-1]
    return modulepath, functionname



