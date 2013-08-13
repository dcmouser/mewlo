"""
mcontroller.py
The base class for callable controllers that are invoked when activating routes
"""




# helper imports
from helpers.callables import find_callable

# mewlo imports
from mexception import mreraise

# python imports
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
        self.parent = None
        self.site = None
        #
        # if they gave us an actual package as root and a function string, we COULD try to do a lookup right now in order to throw an early exception
        # otherwise we will defer lookup until later
        if (True):
            if (root != None and isinstance(function,basestring)):
                self.callable = find_callable(root, function)



    def get_controllerroot(self):
        return self.root
    def get_parent(self):
        return self.parent

    def prepare(self, parent, site, eventlist):
        """Do initial preparatory stuff on system startup."""
        # ATTN: todo - use eventlist

        self.parent = parent
        self.site= site
        # we want to propagage callableroot from parent down
        if (self.root==None):
            self.root = parent.get_controllerroot()
        # now calculate callable once instead of every time
        if (self.callable==None):
            self.callable = self.find_ourcallable()



    def find_ourcallable(self):
        """Lookup the callable wrapped by this controller object."""

        if (self.function==None):
            # error, nothing to call
            raise Exception("No function specified for callable.")
        elif (not isinstance(self.function, basestring)):
            # they gave us a function directly, just use it
            return self.function
        else:
            # they gave us a string, so we're going to look it up at root
            callablestring = self.function

        # look it up by string
        try:
            callable = find_callable(self.get_controllerroot(), callablestring)
        except Exception as exp:
            # add some info and reraise
            mreraise(exp, "Error occurred while trying to look up the callable '"+callablestring+"' specified by: ", obj=self)

        return callable



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


