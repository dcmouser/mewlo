# mroutemanager.py
# This file contains classes to support hierarchical settings associates with sites




















class MewloRoute(object):
    """
    The MewloRouteManager class keeps track of url routes
    """

    def __init__(self, in_routemanager, in_routedict = {}):
        self.routemanager = in_routemanager
        self.routedict = in_routedict


    def get(self, keyname, defaultval=None):
        if (keyname in self.routedict):
            return self.routedict[keyname]
        return defaultval



    def process_request(self, request):
        # return True if the request is for this site and we have set request.response
        if (self.get("path") == request.get_path()):
            # match, we handle it
            self.handle_request(request)
            return True
        # not handled
        return False



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





