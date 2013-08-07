# mcontroller.py
# The base class for callable controllers that are invoked when activating routes


# helpers
from helpers.callables import find_callable, find_callable_throwexception

# python modules
from types import ModuleType



class MewloController(object):
    """
    The MewloController class stores a hierarchical dictionary of settings
    """

    def __init__(self, function = None, root = None):
        self.function = function
        self.root = root
        #
        self.callable = None
        self.parentobj = None
        self.site = None
        #
        # if they gave us an actual package as root and a function string, we COULD try to do a lookup right now in order to throw an early exception
        # otherwise we will defer lookup until later
        if (True):
            #if (isinstance(root,ModuleType) and isinstance(function,basestring)):
            if (root != None and isinstance(function,basestring)):
                self.callable = find_callable_throwexception(root, function)



    def get_controllerroot(self):
        return self.root



    def prepare(self, parentobj, site, errors):
        """Do initial preparatory stuff on system startup."""

        self.parentobj = parentobj
        self.site= site
        # we want to propagage callableroot from parent down
        if (self.root==None):
            self.root = parentobj.get_controllerroot()
        # now calculate callable once instead of every time
        if (self.callable==None):
            (self.callable, errorstr) = self.find_callable()
            if (self.callable == None):
                errors.error(errorstr)



    def find_callable(self):
        """Lookup the callable wrapped by this controller object."""

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
        (callable, errorstr) = find_callable(self.get_controllerroot(), callablestring)
        if (errorstr!=""):
            errorstr = "In route '"+self.parentobj.id+"' of site '"+self.site.get_sitename()+"', "+errorstr
        return (callable, errorstr)



    def invoke(self, request):
        """
        Invoke callable on the request.
        Sublassed could implement this differently
        :return: (successflag, errorstr)
        """

        return self.callable(request)



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"MewloController:\n"
        outstr += indentstr+" callable: "+str(self.callable)+"\n"
        return outstr


