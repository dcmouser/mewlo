# mroutemanager.py
# This file contains classes to support hierarchical settings associates with sites


# mewlo modules
from mewlo.mpackages.core.mcontroller import MewloController





class MewloRouteArg(object):
    """The MewloRouteArg represents a single route argument"""

    def __init__(self, id, required, positional, help, defaultval):
        self.id = id
        self.required = required
        self.positional = positional
        self.help = help
        self.defaultval = defaultval



    def validate_argvalue(self, argval):
        """
        Check arg type and value
        @return tuple (isvalid, argval, errorstr)
        where isvalid is True if it meets requirements, or False if not
        where argval is CONVERTED/COERCED argval
        where errorstr is "" on valid, or description of error if not
        note that argval will ONLY be CONVERTED IFF isvalid is returned as true, i.e. it is safely MADE valid; this will happen most typically for INTEGER args
        """

        isvalid = False
        errorstr = "Base MewloRouteArg cannot be used as an actual instantiated arg."
        return (isvalid, argval, errorstr)



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"MewloRouteArg '"+self.id+"':\n"
        outstr += indentstr+" argtype: "+self.get_argtypestr()+"\n"
        outstr += indentstr+" required: "+str(self.required)+"\n"
        outstr += indentstr+" positional: "+str(self.required)+"\n"
        outstr += indentstr+" help: "+str(self.help)+"\n"
        return outstr



    def get_isflag(self):
        """Return true if this arg type is a flag; base class returns False; subclasses may override."""
        return False










class MewloRouteArgFlag(MewloRouteArg):
    """The MewloRouteArg represents a single route argument"""

    def __init__(self, id, required=True, positional=False, help=None, defaultval=None):
        # just defer to parent constructor
        super(MewloRouteArgFlag, self).__init__(id, required=required, positional=positional, help=help, defaultval=defaultval)


    def validate_argvalue(self, argval):
        # see parent class for documentation
        isvalid = (type(argval) == bool)
        if (not isvalid):
            errorstr = "Expected boolean True/False."
        else:
            errorstr = ""
        return (isvalid, argval, errorstr)


    def get_isflag(self):
        return True


    def get_argtypestr(self):
        return "Flag"





class MewloRouteArgString(MewloRouteArg):
    """The MewloRouteArg represents a single route argument"""

    def __init__(self, id, required=True, positional=False, help=None, defaultval=None):
        # just defer to parent constructor
        super(MewloRouteArgString, self).__init__(id, required=required, positional=positional, help=help, defaultval=defaultval)


    def validate_argvalue(self, argval):
        # see parent class for documentation
        isvalid = True
        errorstr = ""
        return (isvalid, argval, errorstr)


    def get_argtypestr(self):
        return "String"





class MewloRouteArgInteger(MewloRouteArg):
    """The MewloRouteArg represents a single route argument"""

    def __init__(self, id, required=True, positional=False, help=None, defaultval=None):
        # just defer to parent constructor
        super(MewloRouteArgInteger, self).__init__(id, required=required, positional=positional, help=help, defaultval=defaultval)


    def validate_argvalue(self, argval):
        # see parent class for documentation
        try:
            argval = int(argval)
            isvalid = True
            errorstr = ""
        except ValueError:
            isvalid = False
            errorstr = "Expected integer value; "+str(ValueError)
        return (isvalid, argval, errorstr)


    def get_argtypestr(self):
        return "Integer"












class MewloRoute(object):
    """
    The MewloRoute class represents a single route
    """

    # class constants
    DEF_ARGID_extraargs = "extraargs"


    def __init__(self, id, path, controller, args=[], allow_extra_args=False, extra = None, forcedargs = None):
        self.id = id
        self.path = path
        self.args = args
        self.allow_extra_args = allow_extra_args
        self.extra = extra
        self.forcedargs = forcedargs
        #
        self.controllerroot = None
        #
        # the controller should be a MewloController derived class, or createable from whatever is passed
        if (isinstance(controller,MewloController)):
            self.controller = controller
        else:
            self.controller = MewloController(function=controller)



    def get_controllerroot(self):
        return self.controllerroot
    def get_extra(self):
        return self.extra



    def prepare(self, parentobj, site, errors):
        """Prepare any info/caching; this is called before system startup by our parent site."""

        self.parentobj = parentobj
        self.site= site
        # root propagation
        if (self.controllerroot==None):
            self.controllerroot = parentobj.get_controllerroot()
        # prepare controller
        if (self.controller!=None):
            self.controller.prepare(self, site, errors)



    def process_request(self, request, site):
        """
        Called to see if we this route matches the request.
        :return: True if the request is for this site and we have set request.response
        :return: False if we fail to match
        """

        routepath = self.path
        requestpath = request.get_path()
        routepathlen = len(routepath)
        requestpathlen = len(requestpath)
        requestextra = ""

        # routepath must be <= len of requestpath
        if (routepathlen>requestpathlen):
            return False

        # exact match?
        if (requestpath == routepath):
            # exact match, there is no arg part
            requestextra = ""
        elif ( (requestpath[:routepathlen]==routepath[:routepathlen]) and (requestpath[routepathlen] == '/') ):
            # we might have some args
            requestextra = requestpath[routepathlen+1:]
        else:
            # no match
            return False

        # ok we got a leftmost match, now we need to check extra argstring parts, separated by '/' character
        (didmatch, argdict, errorstr) = self.match_args(requestextra)

        # ok, did we match? if so handle it
        if (didmatch):
            handleresult = self.handle_request(request, site, argdict)

        # return flag saying if we matched
        return didmatch



    def match_args(self, requestargstring):
        """
        Split argstring into '/' separated args and try to match against route args.
        @return tuple(didmatchargs, argdict, errorstr), where:
        * didmatchargs is True on match or False on no match
        * argdict is a dictionary with argid = value entries
        * errorstr is "" on success, or an errorstring on failure
        if didmatchargs = False, then caller should treat errorstr as explanation for failure to match rather than as an error per se
        """

        argdict = {}
        errorstr = ""

        # remove any trailing '/'
        requestargstringlen = len(requestargstring)
        if (requestargstringlen>0 and requestargstring[requestargstringlen-1]=='/'):
            requestargstring = requestargstring[:requestargstringlen-1]
        # split argstring into '/' separated words
        if (requestargstring == ""):
            requestargs = []
        else:
            requestargs = requestargstring.split('/')
        requestargcount = len(requestargs)

        # now walk route args and try to consume
        routeargs = self.args
        requestargindex = 0
        #
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
                        errorstr = "Route arg "+argid+" was found but without an associated value following it."
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
                    errorstr = "Route arg "+argid+" was required but not found in request."
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
                (isvalid, argval, typecheckerrorstr) = routearg.validate_argvalue(argval)
                if (isvalid):
                    # assign arg value in dictionary
                    argdict[argid]=argval
                else:
                    # error in value type
                    errorstr = "Route arg "+argid+" did not match expected value type: " + typecheckerrorstr
                    break

        # ok we've walked all the route args, if there was no error, we can proceed to final stage, checking for extra args at end of expected route args
        if (errorstr == ""):
            # ok got all the args we REQUIRED, now is there extra stuff?
            if (requestargindex < requestargcount):
                # there are extra parts, is this allowed?
                if (self.allow_extra_args):
                    # ok consume the extra args and store them as a list in the argdict assigned to a special arg id
                    argdict[self.DEF_ARGID_extraargs] = requestargs[requestargindex:]
                else:
                    # extra args are considered errors
                    errorstr = "Extra args found at end of request after matching all expected args in route."

        # if there were no errors then it's a match, otherwise it's failure to match
        if (errorstr == ""):
            didmatch = True
        else:
            didmatch = False

        # return
        return (didmatch, argdict, errorstr)



    def handle_request(self, request, site, argdict):
        """We matched against this route, so WE will handle the request."""

        # any args in argdict that need to be FORCED?
        self.force_args(argdict)

        # update the request and record the matched site, parsed arg dictionary, etc
        request.set_matched(self, site)
        request.set_route_parsedargs(argdict)

        # give site a chance to pre-handle the invocation
        precall_success = site.pre_runroute_callable(self, request)
        if (not precall_success):
            return False

        # ok now we want to call whatever function should do the actual work
        (success, errorstr) = self.invoke_routecall(request)

        # give site a chance to pre-handle the invocation
        poistcall_success = site.post_runroute_callable(request)

        # error?
        if (not success):
            responsedata = "Found a route that handled it: '"+self.id+"' but got error when trying to invoke route controller.  Error: "+errorstr+"."
            request.response.set_responsedata(responsedata)

        # return success
        return success



    def invoke_routecall(self, request):
        """
        Invoke the specified function by route string
        This requires a little bit of magic, since we are going to launch the function given its dotted path name
        """

        if (self.controller==None):
            return (False, "Controller was not found when preparing route.")

        (success, errorstr) = self.controller.invoke(request)
        return (success, errorstr)



    def force_args(self, argdict):
        """Merge in forced args (i use an explicit loop here because argdict is not likely to remain a pure dictionary in future code)."""

        if (self.forcedargs==None):
            return
        for key,val in self.forcedargs.iteritems():
            argdict[key]=val



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"MewloRoute '"+self.id+"':\n"
        outstr += indentstr+" path: "+self.path+"\n"
        if (self.controller!=None):
            outstr += self.controller.debug(indentstr+" ")
        else:
            outstr += indentstr+" Controller: "+str(self.controller)+"\n"
        outstr += indentstr+" args:\n"
        indentstr += " "
        for routearg in self.args:
            outstr += routearg.debug(indentstr+" ")
        return outstr











class MewloRouteGroup(object):
    """
    The MewloRouteGroup class holds a list of routes (or child RouteGroups)
    """

    def __init__(self, controllerroot=None, routes=None):
        self.controllerroot = controllerroot
        self.routes = []
        self.parentobj = None
        self.site = None
        #
        if (routes != None):
            self.append(routes)


    def get_controllerroot(self):
        return self.controllerroot
    def set_controllerroot(self, controllerroot):
        self.controllerroot = controllerroot



    def append(self, routes):
        """Append a new route (or list of routes) (or hierarchical routegroups) to our routes list."""
        if isinstance(routes,list):
            for route in routes:
                self.routes.append(route)
        else:
            self.routes.append(routes)



    def process_request(self, request, site):
        """Walk through the site list and let each site take a chance at processing the request."""
        ishandled = False
        for route in self.routes:
            ishandled = route.process_request(request, site)
            if (ishandled):
                # ok this site handled it
                break
        return ishandled



    def prepare(self, parentobj, site, errors):
        """Initial preparation, invoked by parent."""

        self.parentobj = parentobj
        self.site= site
        # we want to propagage controllerroot from parent down
        if (self.controllerroot==None):
            self.controllerroot = parentobj.get_controllerroot()
        # recursive prepare
        for route in self.routes:
            route.prepare(self, site, errors)



    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = indentstr+"MewloRouteGroup reporting in:\n"
        outstr += indentstr+" Root for controllers: " + str(self.controllerroot)+"\n"
        for route in self.routes:
            outstr += route.debug(indentstr+" ")+"\n"
        return outstr


