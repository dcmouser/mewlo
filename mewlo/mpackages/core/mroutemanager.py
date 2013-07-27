# mroutemanager.py
# This file contains classes to support hierarchical settings associates with sites




















class MewloRoute(object):
    """
    The MewloRouteManager class keeps track of url routes
    """

    # class constants
    DEF_ROUTE_PROPNAME_ALLOWEXTRAARGS = "allow_extra_args"
    DEF_ROUTE_ARGTYPE_FLAG = "FLAG"
    DEF_ROUTE_ARGTYPE_STRING = "STRING"
    DEF_ROUTE_ARGTYPE_INTEGER = "INTEGER"
    DEF_ROUTE_VIRTUALARGID_EXTRAARGS = "__EXTRAARGS"


    def __init__(self, in_routemanager, in_routedict = {}):
        self.routemanager = in_routemanager
        self.routedict = in_routedict


    def get(self, keyname, defaultval=None):
        if (keyname in self.routedict):
            return self.routedict[keyname]
        return defaultval

    def get_path(self):
        return self.get("path")


    def get_routeargs(self):
        return self.get("args",[])



    def process_request(self, request):
        # return True if the request is for this site and we have set request.response
        # we can return false as soon as we fail to match

        routepath = self.get_path()
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
            self.handle_request(request)

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

        #
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
        routeargs = self.get_routeargs()
        requestargindex = 0
        #
        for routearg in routeargs:
            # does this arg match the name (or position)?
            didmatcharg = False
            argid = routearg.get("id")
            argtype = routearg.get("type",self.DEF_ROUTE_ARGTYPE_STRING)
            argrequired = routearg.get("required",True)
            #
            if ((requestargindex < requestargcount) and (argid == requestargs[requestargindex]) ):
                # ok we matched this arg, assign it, consume it, and move to next
                didmatcharg = True
            if (didmatcharg):
                # we matched it so we will now try to consume it from request args and move to next
                # but first we have to make sure its either a FLAG or it has a value next in the request arg list
                if (argtype==self.DEF_ROUTE_ARGTYPE_FLAG):
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
                (isvalid, argval, typecheckerrorstr) = self.check_and_convert_argvalue_against_argtype(argtype,argval)
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
                allowextraargs = self.get(self.DEF_ROUTE_PROPNAME_ALLOWEXTRAARGS,False)
                if (allowextraargs):
                    # ok consume the extra args and store them as a list in the argdict assigned to a special arg id
                    argdict[self.DEF_ROUTE_VIRTUALARGID_EXTRAARGS] = requestargs[requestargindex:]
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







    def check_and_convert_argvalue_against_argtype(self, argtype, argval):
        """
        Check arg type and value
        @return tuple (isvalid, errorstr)
        where isvalid is True if it meets requirements, or False if not
        where argval is CONVERTED/COERCED argval
        where errorstr is "" on valid, or description of error if not
        note that argval will ONLY be CONVERTED IFF isvalid is returned as true, i.e. it is safely MADE valid; this will happen most typically for INTEGER args
        """
        isvalid = False
        errorstr = ""
        #
        if (argtype == self.DEF_ROUTE_ARGTYPE_STRING):
            isvalid = True
        elif (argtype == self.DEF_ROUTE_ARGTYPE_FLAG):
            isvalid = (type(argval) == bool)
            if (not isvalid):
                errorstr = "Expected boolean True/False."
        elif (argtype == self.DEF_ROUTE_ARGTYPE_INTEGER):
            try:
                argval = int(argval)
                isvalid = True
            except ValueError:
                errorstr = "Expected integer value; "+str(ValueError)
        #
        return (isvalid, argval, errorstr)



    def handle_request(self,request):
        # we handle the request
        request.response.set_responsedata("Found a route that handled it: "+self.get("id","anonymous"))








    def debug(self, indentstr=""):
        outstr = indentstr+"MewloRoute: "
        outstr += indentstr+str(self.routedict)+"\n"
        return outstr



















class MewloRouteManager(object):
    """
    The MewloRouteManager class keeps track of url routes
    """

    def __init__(self, in_site):
        self.routes = []
        #
        self.site = in_site


    def add_route(self, in_routedict):
        route = MewloRoute(self, in_routedict)
        self.routes.append(route)






    def process_request(self, request):
        # walk through the site list and let each site take a chance at processing the request
        ishandled = False
        for route in self.routes:
            ishandled = route.process_request(request)
            if (ishandled):
                # ok this site handled it
                break
        return ishandled





    def debug(self, indentstr=""):
        outstr = indentstr+"MewloRouteManager reporting in.\n"
        indentstr += " "
        outstr += indentstr+"Url Routes:\n"
        for route in self.routes:
            outstr += route.debug(indentstr+" ")
        return outstr





