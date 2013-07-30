# mcontroller.py
# The base class for callable controllers that are invoked when activating routes


# helpers
from helpers.callables import findcallable

# python modules
from types import ModuleType



class MewloController(object):
    """
    The MewloController class stores a hierarchical dictionary of settings
    """

    def __init__(self, function = None, root = None):
        self.root = root
        self.function = function
        #
        self.callable = None
        self.parentobj = None
        self.site = None
        #
        # if they gave us an actual package as root and a function string, we COULD try to do a lookup right now in order to throw an early exception
        # otherwise we will defer lookup until later
        if (True):
            if (isinstance(root,ModuleType) and isinstance(function,basestring)):
                self.callable = findcallable(root, function, True)


    def get_controllerroot(self):
        return self.root


    def prepare(self, parentobj, site, errors):
        # update stuff for ourself based on parent
        self.parentobj = parentobj
        self.site= site
        # we want to propagage callableroot from parent down
        if (self.root==None):
            self.root = parentobj.get_controllerroot()
        # now calculate callable once instead of every time
        if (self.callable==None):
            (self.callable, errorstr) = self.find_callable()
            if (self.callable == None):
                errors.add_errorstr(errorstr)




    def find_callable(self):
        # look up the callable
        if (self.function==None):
            # error, nothing to call
            return (None,"No function specified for callable.")
        elif (not isinstance(self.function, basestring)):
            # they gave us a function directly, just use it
            return (self.function,"")
        else:
            # they gave us a string, so we're going to look it up at root
            callablestring = self.function

        # look it up by string
        (callable, errorstr) = findcallable(self.get_controllerroot(), callablestring, False)
        if (errorstr!=""):
            errorstr = "In route '"+self.parentobj.id+"' of site '"+self.site.get_sitename()+"', "+errorstr
        return (callable, errorstr)




    def invoke(self, request):
        # just invoke callable
        return self.callable(request)



    def debug(self, indentstr=""):
        outstr = indentstr+"MewloController:\n"
        outstr += indentstr+" callable: "+str(self.callable)+"\n"
        return outstr