# mroutemanager.py
# This file contains classes to support hierarchical settings associates with sites




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


    def debug(self, indentstr=""):
        outstr = indentstr+"MewloRouteManager reporting in.\n"
        indentstr += " "
        outstr += indentstr+"Url Routes:\n"
        for route in self.routes:
            outstr += route.debug(indentstr+" ")
        return outstr









class MewloRoute(object):
    """
    The MewloRouteManager class keeps track of url routes
    """

    def __init__(self, in_routemanager, in_routedict = {}):
        self.routemanager = in_routemanager
        self.routedict = in_routedict




    def debug(self, indentstr=""):
        outstr = indentstr+"MewloRoute: "
        outstr += indentstr+str(self.routedict)+"\n"
        return outstr