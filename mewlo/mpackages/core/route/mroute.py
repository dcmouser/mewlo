"""
mroute.py
This file contains classes to support url routes
"""


# mewlo imports
from .. import mglobals
from ..controller import mcontroller
from ..eventlog.mevent import EFailure, EFailureExtend
from ..manager import manager



class MewloRouteArg(object):
    """The MewloRouteArg represents a single route argument."""

    def __init__(self, id, required, positional, help, defaultval):
        self.id = id
        self.required = required
        self.positional = positional
        self.help = help
        self.defaultval = defaultval



    def validate_argvalue(self, argval):
        """
        Check arg type and value.
        :return: tuple (argval, failure)
        where argval is CONVERTED/COERCED argval, or None on failure
        """
        return None, EFailure("Base MewloRouteArg cannot be used as an actual instantiated arg.")



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloRouteArg '" + self.id + "':\n"
        outstr += " "*indent + " argtype: " + self.get_argtypestr()+"\n"
        outstr += " "*indent + " required: " + str(self.required)+"\n"
        outstr += " "*indent + " positional: " + str(self.required)+"\n"
        outstr += " "*indent + " help: " + str(self.help)+"\n"
        return outstr



    def get_isflag(self):
        """Return true if this arg type is a flag; base class returns False; subclasses may override."""
        return False


    def get_argtypestr(self):
        """Just nice label for display."""
        return "None (base arg class)"








class MewloRouteArgFlag(MewloRouteArg):
    """The MewloRouteArg represents a single route argument."""

    def __init__(self, id, required=True, positional=False, help=None, defaultval=None):
        # just defer to parent constructor
        super(MewloRouteArgFlag, self).__init__(id, required=required, positional=positional, help=help, defaultval=defaultval)


    def validate_argvalue(self, argval):
        # see parent class for documentation
        try:
            argval = int(argval)
        except Exception as exp:
            return None, EFailure("Expected boolean value; " + str(exp))
        return argval, None


    def get_isflag(self):
        return True

    def get_argtypestr(self):
        """Just nice label for display."""
        return 'Flag'





class MewloRouteArgString(MewloRouteArg):
    """The MewloRouteArg represents a single route argument."""

    def __init__(self, id, required=True, positional=False, help=None, defaultval=None):
        # just defer to parent constructor
        super(MewloRouteArgString, self).__init__(id, required=required, positional=positional, help=help, defaultval=defaultval)


    def validate_argvalue(self, argval):
        # see parent class for documentation
        return argval, None


    def get_argtypestr(self):
        """Just nice label for display."""
        return 'String'





class MewloRouteArgInteger(MewloRouteArg):
    """The MewloRouteArg represents a single route argument."""

    def __init__(self, id, required=True, positional=False, help=None, defaultval=None):
        # just defer to parent constructor
        super(MewloRouteArgInteger, self).__init__(id, required=required, positional=positional, help=help, defaultval=defaultval)


    def validate_argvalue(self, argval):
        # see parent class for documentation
        try:
            argval = int(argval)
        except Exception as exp:
            return None, EFailure("Expected integer value; " + str(exp))
        return argval, None


    def get_argtypestr(self):
        """Just nice label for display."""
        return 'Integer'












class MewloRoute(object):
    """
    The MewloRoute class represents a single route.
    """

    # class constants
    DEF_ARGID_extraargs = 'extraargs'


    def __init__(self, id, path, controller, args=[], allow_extra_args=False, extras = None, forcedargs = None):
        self.id = id
        self.path = path
        self.args = args
        self.allow_extra_args = allow_extra_args
        self.extras = extras
        self.forcedargs = forcedargs
        #
        self.controllerroot = None
        self.mewlosite = None
        #
        # the controller should be a MewloController derived class, or createable from whatever is passed
        if (isinstance(controller, mcontroller.MewloController)):
            self.controller = controller
        else:
            self.controller = mcontroller.MewloController(function=controller)



    def get_controllerroot(self):
        return self.controllerroot
    def get_extras(self):
        return self.extras
    def get_parent(self):
        return self.parent
    def get_id(self):
        return self.id
    def get_mewlosite(self):
        return self.mewlosite
    def get_routegroup(self):
        return self.parent


    def startup(self, parent, mewlosite, eventlist):
        """Startup any info/caching; this is called before system startup by our parent site."""

        self.parent = parent
        self.mewlosite = mewlosite
        # root propagation
        if (self.controllerroot == None):
            self.controllerroot = parent.get_controllerroot()
        # startup controller
        if (self.controller != None):
            self.controller.startup(self, eventlist)
        # modify path based on pathprefix
        pathprefix = self.get_routegroup().get_pathprefix()
        if (pathprefix!=None):
            self.path = pathprefix + self.path


    def shutdown(self):
        """Any shutdown procedures to perform?"""
        if (self.controller != None):
            self.controller.shutdown()


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloRoute '" + self.id + "':\n"
        outstr += " "*indent + " path: " + self.path + "\n"
        indent += 1
        if (self.controller != None):
            outstr += self.controller.dumps(indent)
        else:
            outstr += " "*indent + "Controller: None.\n"
        outstr += " "*indent + "Route Args: "
        if (len(self.args)==0):
            outstr += "None.\n"
        else:
            outstr += "\n"
        for routearg in self.args:
            outstr += routearg.dumps(indent+1)
        return outstr




    def get_isgroup(self):
        return False


    def process_request(self, mewlosite, request):
        """
        Called to see if we this route matches the request.
        :return: True if the request is for this site and we have set request.response
        :return: False if we fail to match
        """

        routepath = self.path
        requestpath = request.get_urlpath()
        routepathlen = len(routepath)
        requestpathlen = len(requestpath)
        requestextra = ''

        # routepath must be <= len of requestpath
        if (routepathlen > requestpathlen):
            return False

        # exact match?
        if (requestpath == routepath):
            # exact match, there is no arg part
            requestextra = ""
        elif ( (requestpath[:routepathlen] == routepath[:routepathlen]) and (requestpath[routepathlen] == '/') ):
            # we might have some args
            requestextra = requestpath[routepathlen+1:]
        else:
            # no match
            return False

        # ok we got a leftmost match, now we need to check extra argstring parts, separated by '/' character
        (didmatch, argdict, failure) = self.match_args(requestextra)

        #if (failure):
        #    print "ATTN: **************** TEST FAILURED ROUTE: " + str(failure) + "\n"

        # ok, did we match? if so handle it
        if (didmatch):
            failure = self.handle_request(mewlosite, request, argdict)

        # return flag saying if we matched
        return didmatch



    def match_args(self, requestargstring):
        """
        Split argstring into '/' separated args and try to match against route args.
        :return: tuple(didmatchargs, argdict, failure), where:
            * didmatchargs is True on match or False on no match.
            * argdict is a dictionary with argid = value entries.
            * failure is None on success
        if didmatchargs = False, then caller should treat failure as explanation for failure to match rather than as an error per se.
        ATTN: we may want to rewrite this and not use failure = EFailure() on "failure" because this is inefficient when frequenly it just means it didn't match the route and we don't care about the failure code and it is just ignored; though it might be useful for debugging purposes sometimes.
        """

        argdict = {}
        failure = None

        # remove any trailing '/'
        requestargstringlen = len(requestargstring)
        if (requestargstringlen > 0 and requestargstring[requestargstringlen-1] == '/'):
            requestargstring = requestargstring[:requestargstringlen-1]

        # ATTN: TODO - UNFINISHED
        # We would like to split off any ? old-style parameter assignments

        # split argstring into '/' separated words
        if (requestargstring == ''):
            requestargs = []
        else:
            requestargs = requestargstring.split('/')
        requestargcount = len(requestargs)

        # now walk route args and try to consume
        routeargs = self.args
        requestargindex = 0

        for routearg in routeargs:
            # does this arg match the name (or position)?
            didmatcharg = False
            argid = routearg.id
            argisflag = routearg.get_isflag()
            argrequired = routearg.required
            argpositional = routearg.positional
            #
            argval = None
            flag_setargval = False
            #
            if ((requestargindex < requestargcount) and (argpositional or (argid == requestargs[requestargindex])) ):
                # ok we matched this arg, assign it, consume it, and move to next
                didmatcharg = True
            if (didmatcharg):
                # we matched it so we will now try to consume it from request args and move to next
                # but first we have to make sure its either a FLAG or it has a value next in the request arg list
                if (argpositional):
                    # positional args just get eaten and assigned
                    argval = requestargs[requestargindex]
                elif (argisflag):
                    # it's a flag so just set flag arg to True and move on
                    argval = True
                else:
                    # it's not a flag, so we REQUIRE next token in request to be the value
                    requestargindex += 1
                    if (requestargindex >= requestargcount):
                        # but there are no more args, so this is an error
                        failure = EFailure("Route arg '{0}' was found but without an associated value following it.".format(argid))
                        break
                    else:
                        # ok we go its value
                        argval = requestargs[requestargindex]
                # set flag saying we have argval ready and to set it below
                flag_setargval = True
                # and advance/consume the request arg index since we matched it
                requestargindex += 1
            else:
                # we didn't match it, so if it was required, it's an error (if it wasn't required, just skip over it)
                if (argrequired):
                    # it was required, and is missing, so that's a FAIL
                    failure = EFailure("Route arg '{0}' was required but not found in request.".format(argid))
                    break
                else:
                    # no value specified, is there a default setting?
                    if (routearg.defaultval):
                        # set flag saying we have argval ready and to set it below
                        argval = routearg.defaultval
                        flag_setargval = True

            # now record the argval
            if (flag_setargval):
                # now let's check to make sure arg value is allowed given arg type
                (argval, argcheckfailure) = routearg.validate_argvalue(argval)
                if (argcheckfailure == None):
                    # assign arg value in dictionary
                    argdict[argid] = argval
                else:
                    # error in value type
                    failure = EFailureExtend(argcheckfailure, "Route arg '{0}' did not match expected value type.".format(argid))
                    break

        # ok we've walked all the route args, if there was no error, we can proceed to final stage, checking for extra args at end of expected route args
        if (failure == None):
            # ok got all the args we REQUIRED, now is there extra stuff?
            if (requestargindex < requestargcount):
                # there are extra parts, is this allowed?
                if (self.allow_extra_args):
                    # ok consume the extra args and store them as a list in the argdict assigned to a special arg id
                    argdict[MewloRoute.DEF_ARGID_extraargs] = requestargs[requestargindex:]
                else:
                    # extra args are considered errors
                    failure = EFailure("Extra args found at end of request after matching all expected args in route.")

        # if there were no errors then it's a match, otherwise it's failure to match
        if (failure == None):
            didmatch = True
        else:
            didmatch = False

        # returnfailf
        return (didmatch, argdict, failure)



    def handle_request(self, mewlosite, request, argdict):
        """We matched against this route, so WE will handle the request."""

        # any args in argdict that need to be FORCED?
        self.force_args(argdict)

        # update the request and record the matched site, parsed arg dictionary, etc
        request.set_matched(self, mewlosite)
        request.set_route_parsedargs(argdict)

        # give site a chance to pre-handle the invocation
        precall_failure = mewlosite.pre_runroute_callable(self, request)
        if (precall_failure != None):
            return precall_failure

        # ok now we want to call whatever function should do the actual work
        call_failure = self.invoke_routecall(request)
        if (call_failure != None):
            return call_failure

        # give site a chance to do something after we run the route
        postcall_failure = mewlosite.post_runroute_callable(request)
        if (postcall_failure != None):
            return postcall_failure

        # return None for success
        return None



    def invoke_routecall(self, request):
        """
        Invoke the specified function by route string
        This requires a little bit of magic, since we are going to launch the function given its dotted path name
        """

        controllerp = self.controller

        if (controllerp == None):
            return EFailure("Controller was not found when preparing route.", obj=self)
        if (not controllerp.get_isenabled()):
            return EFailure("Controller for this route is not enabled.", obj=self)

        return self.controller.invoke(request)



    def force_args(self, argdict):
        """Merge in forced args (i use an explicit loop here because argdict is not likely to remain a pure dictionary in future code)."""

        if (self.forcedargs == None):
            return
        for (key, val) in self.forcedargs.iteritems():
            argdict[key] = val





    def construct_url(self):
        """Construct a url for this route.
        ATTN: TODO - this is preliminary version; eventually we will want to be able to accept info for context so we can fill parameters."""
        return self.mewlosite.relative_url(self.path)







class MewloRouteGroup(object):
    """
    The MewloRouteGroup class holds a list of routes (or child RouteGroups); it's a way of letting us organize collections of routes
    """

    def __init__(self, id='', controllerroot=None, routes=None):
        self.id = id
        self.controllerroot = controllerroot
        self.routes = []
        #
        self.parent = None
        self.mewlosite = None
        self.routehash = {}
        #
        self.pathprefix = ''
        #
        if (routes != None):
            self.append(routes)


    def startup(self, parent, mewlosite, eventlist):
        """Initial preparation, invoked by parent."""

        self.parent = parent
        # we want to propagate controllerroot from parent down
        if (self.controllerroot == None):
            self.controllerroot = parent.get_controllerroot()
        # recursive startup
        for route in self.routes:
            route.startup(self, mewlosite, eventlist)



    def shutdown(self):
        """Shutdown, invoked by parent."""
        for route in self.routes:
            route.shutdown()


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloRouteGroup reporting in:\n"
        outstr += " "*indent + " Root for controllers: " + str(self.controllerroot) + "\n"
        outstr += " "*indent + " Path prefix: " + self.pathprefix + "\n"
        outstr += " "*indent + " Route hash: " + str(self.routehash) + "\n"
        outstr += "\n"
        for route in self.routes:
            outstr += route.dumps(indent+1) + "\n"
        return outstr




    def get_isgroup(self):
        return True

    def get_controllerroot(self):
        return self.controllerroot
    def set_controllerroot(self, controllerroot):
        self.controllerroot = controllerroot
    def set_pathprefix(self, pathprefix):
        self.pathprefix = pathprefix
    def get_pathprefix(self):
        return self.pathprefix
    def get_parent(self):
        return self.parent


    def append(self, routes):
        """Append a new route (or list of routes) (or hierarchical routegroups) to our routes list."""
        if isinstance(routes, list):
            for route in routes:
                self.routes.append(route)
        else:
            self.routes.append(routes)



    def process_request(self, mewlosite, request):
        """Walk through the site list and let each site take a chance at processing the request."""
        ishandled = False
        for route in self.routes:
            ishandled = route.process_request(mewlosite, request)
            if (ishandled):
                # ok this site handled it
                break
        return ishandled



    def build_routehash(self):
        """Build hash of all routes in entire collection."""
        self.routehash = {}
        for route in self.routes:
            if (route.get_isgroup()):
                childroutehash = route.build_routehash()
                if (route.id==None or route.id==''):
                    # just merge it into us
                    self.routehash.update(childroutehash)
                else:
                    # add with prefix
                    prefix = route.id + '.'
                    for key,val in childroutehash.iteritems():
                        self.routehash[prefix+key]=val
            else:
                # it's a leaf route
                self.routehash[route.id] = route
        return self.routehash


    def lookup_route_byid(self, routeid):
        """Lookup routeid in our hash of all routes."""
        if (routeid in self.routehash):
            return self.routehash[routeid]
        return None








class MewloRouteManager(manager.MewloManager):
    """
    The MewloRouteManager class manages the routes in a site; it is a thin class that owns a single route group
    """

    def __init__(self, mewlosite, debugmode):
        super(MewloRouteManager,self).__init__(mewlosite, debugmode)
        self.routegroup = MewloRouteGroup('', None, None)


    def startup(self, eventlist):
        super(MewloRouteManager,self).startup(eventlist)
        self.routegroup.startup(self.mewlosite, self.mewlosite, eventlist)
        self.routegroup.build_routehash()


    def shutdown(self):
        super(MewloRouteManager,self).shutdown()
        self.routegroup.shutdown()



    def append(self, routes):
        """Append a new route (or list of routes) (or hierarchical routegroups) to our routes list."""
        return self.routegroup.append(routes)

    def process_request(self, mewlosite, request):
        """Walk through the site list and let each site take a chance at processing the request."""
        return self.routegroup.process_request(mewlosite,request)






    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloRouteManager reporting in:\n"
        #outstr += " "*indent + " Routegroup: ers: " + str(self.controllerroot) + "\n"
        outstr += self.routegroup.dumps(indent+1) + "\n"
        return outstr



    def lookup_route_byid(self, routeid):
        """Lookup routeid in our hash of all routes."""
        return self.routegroup.lookup_route_byid(routeid)

