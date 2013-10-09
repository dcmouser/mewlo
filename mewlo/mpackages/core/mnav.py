"""
mnav.py
This module contains classes that handle the site navigational hierarchy and pages.
"""


# mewlo imports


# helper imports


# python imports



class NavNodeManager(object):
    """
    The NavNodeManager class manages a collection of NavNodes.
    The most common usage would be that each site has a NavNodeManager to represent the site hierarchy
    """

    def __init__(self):
        """Constructor for the clas."""
        self.nodes = []


    def startup(self, eventlist):
        """Called at start of application."""
        pass

    def shutdown(self):
        """Called at shutdown of application."""
        pass


    def add_nodes(self, nodestoadd):
        """Add one or more nodes to our node list."""
        if type(nodestoadd) is list:
            self.nodes.extend(nodestoadd)
        else:
            self.nodes.append(nodestoadd)


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""

        outstr = " "*indent + "NavNodeManager reporting in with {0} nodes:\n".format(len(self.nodes))
        indent += 1
        for node in self.nodes:
            outstr += node.dumps(indent)
        #
        return outstr










class NavNode(object):
    """
    The NavNode class represents a page on the site.
    Every page on the site should map to a NavNode object.
    The hierarchical structure of the site can be specified with regard to NavNodes.
    NavNodes are used:
        * To store page titles.
        * To generate site menus (top navigation menu, sidebar menu, etc.)
        * To generate breadcrumbs.
        * To assist in dynamic url generation.
    """

    def __init__(self, id, properties={}):
        """Constructor for the clas."""
        self.id = id
        self.properties = properties



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""

        outstr = " "*indent + "Navnode {0} reporting in:\n".format(self.id)
        outstr += " "*indent + " properties: "+str(self.properties)
        #
        return outstr







class NavLink(object):
    """
    The NavLink class is a small helper class that is used to refer to a NavNode by id, with its own propertiess.
    It is used when we need to specify children NavNodes and we need to provide additional information.
    """

    def __init__(self, id, properties={}):
        """Constructor for the clas."""
        self.id = id
        self.properties = properties


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""

        outstr = " "*indent + "Navlink {0} reporting in:\n".format(self.id)
        outstr += " "*indent + " properties: "+str(self.properties)
        #
        return outstr


