"""
mcontroller.py
The base class for callable controllers that are invoked when activating routes
"""


# helper imports
from ..eventlog.mexceptionplus import ExceptionPlus, reraiseplus
from ..helpers.callables import find_callable

# python imports
from types import ModuleType





class MewloController(object):
    """
    The MewloController class handles requests that are routed to it.
    """

    def __init__(self, function = None, root = None):
        self.function = function
        self.root = root
        #
        self.callable = None
        self.parent = None
        #
        self.isenabled = False
        #
        # if they gave us an actual pack as root and a function string, we COULD try to do a lookup right now in order to throw an early exception
        # otherwise we will defer lookup until later
        if (True):
            if (root != None and isinstance(function, basestring)):
                self.callable = find_callable(root, function)



    def get_controllerroot(self):
        return self.root
    def get_parent(self):
        return self.parent
    def get_isenabled(self):
        return self.isenabled


    def startup(self, parent, eventlist):
        """Do initial preparatory stuff on system startup."""
        # ATTN: todo - use eventlist to catch errors

        self.parent = parent
        # we want to propagage callableroot from parent down
        if (self.root == None):
            self.root = parent.get_controllerroot()
        # now calculate callable once during preparation (if it wasn't explicitly set during constructor)
        if (self.callable == None):
            self.callable = self.find_ourcallable()
        # disable it if it's not set
        self.isenabled = (self.callable != None)


    def shutdown(self):
        """Shutdown of controller."""
        pass




    def find_ourcallable(self):
        """Lookup the callable wrapped by this controller object."""

        if (self.function == None):
            # error, nothing to call
            raise ExceptionPlus("No function specified for callable.", obj=self)
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
            # ATTN: we currently use an exception here because we treat this like a fatal error
            # If instead we wanted to simply ignore the error return a 500 status error code and keep serving we could return None from here and log error, etc.
            reraiseplus(exp, "Error occurred while trying to look up the callable '{0}' specified by: ".format(callablestring), obj=self)

        # success, return it
        return callable



    def invoke(self, request):
        """
        Invoke callable on the request.
        Sublassed could implement this differently
        :return: failure or None on success
        """

        return self.callable(request, request.response)



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloController ({0}):\n".format(self.__class__.__name__)
        outstr += " "*indent + " callable: " + str(self.callable) + "\n"
        return outstr


