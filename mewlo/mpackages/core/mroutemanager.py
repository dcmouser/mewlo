# mroutemanager.py
# This file contains classes to support hierarchical settings associates with sites


# mewlo modules
from helpers.errortracker import ErrorTracker
from helpers.callables import find_callable_from_dottedpath




















class MewloRouteArg(object):
    """The MewloRouteArg represents a single route argument"""

    def __init__(self, id, argtype, required, positional, help):
        self.id = id
        self.argtype = argtype
        self.required = required
        self.positional = positional
        self.help = help


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
        outstr = indentstr+"MewloRouteArg '"+self.id+"':\n"
        outstr += indentstr+" argtype: "+self.argtype+"\n"
        outstr += indentstr+" required: "+str(self.required)+"\n"
        outstr += indentstr+" positional: "+str(self.required)+"\n"
        outstr += indentstr+" help: "+str(self.help)+"\n"
        return outstr

    def get_isflag(self):
        # subclass may implement
        return False







class MewloRouteArgFlag(MewloRouteArg):
    """The MewloRouteArg represents a single route argument"""
    #
    def __init__(self, id, required=True, positional=False, help=""):
        # just defer to parent constructor (but force argtype just for debugging purposes)
        super(MewloRouteArgFlag, self).__init__(id, argtype="FLAG", required=required, positional=positional, help=help)
    #
    def validate_argvalue(self, argval):
        # see parent class for documentation
        isvalid = (type(argval) == bool)
        if (not isvalid):
            errorstr = "Expected boolean True/False."
        else:
            errorstr = ""
        return (isvalid, argval, errorstr)
    #
    def get_isflag(self):
        return True



class MewloRouteArgString(MewloRouteArg):
    """The MewloRouteArg represents a single route argument"""
    #
    def __init__(self, id, required=True, positional=False, help=""):
        # just defer to parent constructor (but force argtype just for debugging purposes)
        super(MewloRouteArgString, self).__init__(id, argtype="STRING", required=required, positional=positional, help=help)
    #
    def validate_argvalue(self, argval):
        # see parent class for documentation
        isvalid = True
        errorstr = ""
        return (isvalid, argval, errorstr)



class MewloRouteArgInteger(MewloRouteArg):
    """The MewloRouteArg represents a single route argument"""
    #
    def __init__(self, id, required=True, positional=False, help=""):
        # just defer to parent constructor (but force argtype just for debugging purposes)
        super(MewloRouteArgInteger, self).__init__(id, argtype="INTEGER", required=required, positional=positional, help=help)
    #
    def validate_argvalue(self, argval):
        # see parent class for documentation
        try:
            argval = int(argval)
            isvalid = True
            errorstr = ""
        except ValueError:
            isvalid = False
            errorstr = "Expected integer value; "+str(ValueError)
        #
        return (isvalid, argval, errorstr)































class MewloRoute(object):
    """
    The MewloRoute class represents a single route
    """

    # class constants
    DEF_ARGID_extraargs = "extraargs"


    def __init__(self, id, path, callable, args=[], allow_extra_args=False, extra = None, callableroot = None):
        #
        self.id = id
        self.path = path
        self.callablestring = callable
        self.args = args
        self.allow_extra_args = allow_extra_args
        self.extra = extra
        self.callableroot = callableroot
        self.callable = None
        #
        self.parentobj = None



#    def get_sitemodule_relativeimportdir(self):
#        # return site import
#        return self.get_site().get_sitemodule_relativeimportdir()

#    def get_site_controller_importdirpkg(self):
#        return self.get_site().get_site_controller_importdirpkg()
#


    def get_callableroot(self):
        return self.callableroot


    def get_extra(self):
        return self.extra



    def prepare(self, parentobj, errors):
        # update stuff for ourself based on parent
        self.parentobj = parentobj
        # we want to propagage callableroot from parent down
        if (self.callableroot==None):
            self.callableroot = parentobj.get_callableroot()
        # now calculate callable once instead of every time
        (self.callable, errorstr) = self.find_callable()
        if (self.callable == None):
            errors.add_errorstr(errorstr)



    def find_callable(self):
        # look up the callable
        (callable, errorstr) = find_callable_from_dottedpath(self.get_callableroot(), self.callablestring)
        if (callable == None):
            errorstr = "Failed to find dynamic callable '"+self.callablestring+"'; "+errorstr
        return (callable, errorstr)


    def process_request(self, request, site):
        # return True if the request is for this site and we have set request.response
        # we can return false as soon as we fail to match

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
            didmatchargs is True on match or False on no match
            argdict is a dictionary with argid = value entries
            errorstr is "" on success, or an errorstring on failure
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
                # now let's check to make sure arg value is allowed given arg type
                (isvalid, argval, typecheckerrorstr) = routearg.validate_argvalue(argval)
                if (isvalid):
                    # assign arg value in dictionary
                    argdict[argid]=argval
                else:
                    # error in value type
                    errorstr = "Route arg "+argid+" did not match expected value type: " + typecheckerrorstr
                    break
                # and advance request arg index
                requestargindex += 1
            else:
                # we didn't match it, so if it was required, it's an error (if it wasn't required, just skip over it)
                if (argrequired):
                    # it was required, and is missing, so that's a FAIL
                    errorstr = "Route arg "+argid+" was required but not found in request."
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
        # we matched against this route, so WE will handle the request

        # update the request and record the matched site, parsed arg dictionary, etc
        request.set_matched(self, site)
        request.set_route_parsedargs(argdict)

        # ok now we want to call whatever function should do the actual work
        (success, errorstr) = self.invoke_routecall(request)

        # error?
        if (not success):
            responsedata = "Found a route that handled it: '"+self.id+"' but got error when trying to invoke route callable.  Error: "+errorstr+"."
            request.response.set_responsedata(responsedata)

        # return success
        return success







    def invoke_routecall(self, request):
        """
        Invoke the specified function by route string
        This requires a little bit of magic, since we are going to launch the function given its dotted path name
        """

        if (self.callable==None):
            return (False, "Callable '"+self.callablestring+"' was not found when preparing route.")

        (success, errorstr) = self.callable(request)
        return (success, errorstr)









    def debug(self, indentstr=""):
        outstr = indentstr+"MewloRoute '"+self.id+"':\n"
        outstr += indentstr+" path: "+self.path+"\n"
        outstr += indentstr+" callable-as-string: "+self.callablestring+"\n"
        outstr += indentstr+" callable: "+str(self.callable)+"\n"
        outstr += indentstr+" args:\n"
        indentstr += " "
        for routearg in self.args:
            outstr += routearg.debug(indentstr+" ")
        return outstr
































class MewloRouteGroup(object):
    """
    The MewloRouteGroup class holds a list of routes (or child RouteGroups)
    """

    def __init__(self, callableroot=None, routes=None):
        self.callableroot = callableroot
        self.routes = []
        self.parentobj = None
        #
        if (routes != None):
            self.append(routes)

    def get_callableroot(self):
        return self.callableroot
    def set_callableroot(self, callableroot):
        self.callableroot = callableroot


    def append(self, routes):
        # append a new route (or list of routes) (or hierarchical routegroups) to our routes list
        if isinstance(routes,list):
            for route in routes:
                self.routes.append(route)
        else:
            self.routes.append(routes)


    def process_request(self, request, site):
        # walk through the site list and let each site take a chance at processing the request
        ishandled = False
        for route in self.routes:
            ishandled = route.process_request(request, site)
            if (ishandled):
                # ok this site handled it
                break
        return ishandled


    def prepare(self, parentobj, errors):
        # update stuff for ourself based on parent
        self.parentobj = parentobj
        # we want to propagage callableroot from parent down
        if (self.callableroot==None):
            self.callableroot = parentobj.get_callableroot()
        # recursive prepare
        for route in self.routes:
            route.prepare(self, errors)


    def debug(self, indentstr=""):
        outstr = indentstr+"MewloRouteGroup reporting in:\n"
        outstr += indentstr+" Root for callables: " + str(self.callableroot)+"\n"
        for route in self.routes:
            outstr += route.debug(indentstr+" ")+"\n"
        return outstr




















