"""
mnav.py
This module contains classes that handle the site navigational hierarchy and pages.

Every page on the site should map to a NavNode object.
The hierarchical structure of the site can be specified with regard to NavNodes.
NavNodes are used:
    * To store page titles.
    * To generate site menus (top navigation menu, sidebar menu, etc.)
    * To generate breadcrumbs.
    * To assist in dynamic url generation.

NavNodes can contain arbitrary dictionary information to be used as hints to site menus, sidebars, sitemaps, and navigation bars, etc.

An unresolved question is whether navnodes should be an independent thing from Routes, or should a Route be a NavNode?

It might seem that all information in a NavNode would be properly stored in a Route entry, and indeed much of the time this would make sense.

But perhaps the way to think of the difference is that the job of the NavNodes hierarchy is to store information about the outward visual organization and appearance of site menus and navigation bars,
wheras routes are about the internal controllers that respond to user requests.

Some examples of where Routes and NavNodes diverge:
    * Every page shown to the user should be marked as belonging to a specific NavNode, but a given route might have options that generate one of multiple NavNode locations.
    * Multiple routes might send the user to the same NavNode destination page.


We have a few functions for producing json data to use in an html menu/navbar/sidebar creation.

These return a json datastructure (hierarchical list) that should contain all of the hierarchy of data needed by a javascript/template function, to render a site menu.
This data includes node properties
            * label_long = text label (shown when there is room)
            * label_short = text label (when space is tight)
            * label_hint = text label (can be very long text, to be shown on hover)
            * flag_onpath = true if this node is on the current navigational path to our location
            * flag_currentloc = true if this is the current leaf destination of the current page
            * urllink = url link for this item
            * flag_visible = whether this item is visible (note that when making the json navdata, we will NOT generate navnodes for items clearly not visible); but this flag might still be used for ajax functions
            * flag_enabled = whether this item should be shown as disabled
            * children = hierarchical list of children nodes
        Note that eventually we will want any property here to be able to be specified as an ajax function; this allows us to do lazy evaluation of dynamic stuff
"""


# mewlo imports
from ..helpers import misc

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
        self.nodehash = {}
        self.mewlosite = None


    def startup(self, mewlosite, eventlist):
        """Called at start of application."""
        self.mewlosite = mewlosite
        # initial nodes
        self.sitenode = NavNode('site')
        self.orphannode = NavNode('__orphans__')
        startnodes = [self.sitenode, self.orphannode]
        self.add_nodes(startnodes)
        #
        self.buildstructure()


    def shutdown(self):
        """Called at shutdown of application."""
        pass




    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""

        outstr = " "*indent + "NavNodeManager reporting in with {0} nodes:\n".format(len(self.nodes))
        indent += 1
        for node in self.nodes:
            outstr += node.dumps(indent)
        #
        return outstr








    def add_nodes(self, nodestoadd):
        """Add one or more nodes to our node list."""
        if type(nodestoadd) is list:
            self.nodes.extend(nodestoadd)
        else:
            self.nodes.append(nodestoadd)


    def lookupnode(self, nodeid):
        """Lookup node by string or reference."""
        if (nodeid==None):
            return None
        # if its not a string, just return it
        if (not isinstance(nodeid,basestring)):
            return nodeid
        if (nodeid in self.nodehash):
            return self.nodehash[nodeid]
        return None



    def buildstructure(self):
        """Walk all nodes and build link structure using children and parents."""

        # first build the nodehash dict, mapping ids to nodes, and clear node children and parents, and do other setup stuff
        self.nodehash = {}
        for node in self.nodes:
            # add node to nodehash by id for quick lookup
            self.nodehash[node.id] = node
            # reset properties (children,parents) and set mewlosite
            node.resetbuild(self.mewlosite)
            # try to guess or lookup the route
            node.lookup_store_route()

        # now walk nodes and make links
        for node in self.nodes:
            # lookup children by id and convert to node references
            children = node.get_property('children',[],False,None)
            children = self.convert_nodeidlist_to_nodelist(children)
            # now walk children and add them to our children list, and add us to their parent list
            for child in children:
                if (child not in node.children):
                    node.children.append(child)
                if (node not in child.parents):
                    child.parents.append(node)
            # lookup parents by id and convert to node references
            parent = node.get_property('parent',None,False,None)
            if (parent != None):
                parents = [parent]
            else:
                parents = node.get_property('parents',[],False,None)
            parents = self.convert_nodeidlist_to_nodelist(parents)
            # now walk parents and add them to our parent list, and add us to their child list
            for parent in parents:
                if (parent not in node.parents):
                    node.parents.append(parent)
                if (node not in parent.children):
                    parent.children.append(node)

        # now those without parents get orphannode as their parent (only orphannode has no parents)
        for node in self.nodes:
            if (node==self.orphannode or node==self.sitenode):
                continue
            if (len(node.parents)==0):
                node.parents = [self.orphannode]
                self.orphannode.children.append(node)




    def convert_nodeidlist_to_nodelist(self, nodeidlist):
        """Convert a list of id strings to a list of node references."""
        nodelist = []
        for nodeid in nodeidlist:
            node = self.lookupnode(nodeid)
            if (node!=None):
                nodelist.append(node)
        return nodelist










    def find_current_and_root(self, rootnode, responsecontext):
        """Given response and a possible explicit rootnode, find current node and rootnode to use."""
        currentnodeid = responsecontext.get_value('pagenode',None)
        currentnode = self.lookupnode(currentnodeid)
        # decide rootnode
        if (currentnode != None and rootnode == None):
            # find the top parent of this node
            rootnode = currentnode.find_rootparent()
        if (rootnode==None):
            rootnode = currentnode
        return (currentnode, rootnode)


    def find_pathto_rootparent(self, curnode, rootnode, flag_wantspecials):
        """Find the path of nodes that go from rootnode to eventual childnode."""
        nodelist = []
        while (True):
            nodelist.append(curnode)
            if (len(curnode.parents)==0):
                break
            if (curnode == rootnode):
                break
            # ATTN: TODO - we only walk up single parent branch
            curnode = curnode.parents[0]
            if (not flag_wantspecials and (curnode==self.orphannode or curnode==self.sitenode)):
                break
        return nodelist











    # menu/navbar/sidebar helper functions
    # ------------------------------------



    def makenav_activerowlist(self, responsecontext, rootnode = None):
        """
        This makenav_ function returns a list of rows, where each row is a list of nodes.
        We might use this for a top navigation bar menu.
        It starts with the children of the root node, and includes subsequent sub-rows corresponding to the path from the root to the current node.
        So that the last row in the list is the row of siblings to the current node.
        On each row there should be one (and only one) active node).
        """
        # init
        navdata = []
        # get currentnode and rootnode to use
        (currentnode, rootnode) = self.find_current_and_root(rootnode, responsecontext)
        # if nothing to do, return now
        if (currentnode == None):
            # nothing to do, just drop down and return
            return navdata

        # get path from current node up to rootnode (or to farthest ancestor if no rootnode)
        nodepath = self.find_pathto_rootparent(currentnode, rootnode, True)

        #print "ATTN: NODEPATH = "+str(nodepath)

        # build rows, walk from parent down to next to last item (dont do currentnode)
        rows = []
        nodecount = len(nodepath)
        for i in range(nodecount-1,-1,-1):
            parentnode = nodepath[i]
            if (i==0):
                activechildnode = None
            else:
                activechildnode = nodepath[i-1]
            row = self.makenav_activerowlist_onerow(parentnode, activechildnode, responsecontext)
            if (len(row)>0):
                rows.append(row)

        # return it
        navdata = rows
        return navdata



    def makenav_activerowlist_onerow(self, parentnode, activechildnode, responsecontext):
        """Make a list (row) of nodes, using children of parent node, and marking the activechildnode as active."""
        row = []
        children = parentnode.children
        for child in children:
            extraproperties = {
                'flag_active' : (child==activechildnode)
                }
            nodeitem = {
                'node' : child,
                'extraprops' : extraproperties,
                }
            row.append(nodeitem)
        return row





    def makenav_rowlist_to_html(self, rowlist, responsecontext):
        """Take a list of built node rows and return html for them."""
        html = ''
        for row in rowlist:
            rowhtml = self.makenav_noderow_to_html(row, responsecontext)
            html += rowhtml + '\n'
        # wrap in div class
        if (html != ''):
            html = '<div class="nav_bar">\n' + html + '</div> <!-- nav_bar -->'
        return html

    def makenav_noderow_to_html(self, row, responsecontext):
        """Build html from a noderow."""
        html = ''
        labelproplist = ['label']
        for nodeitem in row:
            nodehtml = self.makenav_node_to_html(nodeitem['node'],nodeitem['extraprops'],labelproplist, responsecontext)
            html += nodehtml
        # wrap in div class
        if (html != ''):
            html = '<div class="nav_bar_row">\n<ul>\n' + html + '\n</ul>\n</div> <!-- nav_bar_row -->'
        return html








    def makenav_breadcrumb_list(self, responsecontext, rootnode = None):
        """
        This makenav_ function returns a breadcrumb list of nodes
        """
        # init
        navdata = []
        # get currentnode and rootnode to use
        (currentnode, rootnode) = self.find_current_and_root(rootnode, responsecontext)
        # if nothing to do, return now
        if (currentnode == None):
            # nothing to do, just drop down and return
            return navdata
        # get path from current node up to rootnode (or to farthest ancestor if no rootnode)
        nodepath = self.find_pathto_rootparent(currentnode, rootnode, False)
        # add site home node to end if appropriate
        if (len(nodepath)>0):
            endnode=nodepath[len(nodepath)-1]
            if (endnode.id!='home'):
                if ('home' in self.nodehash):
                    nodepath.append(self.nodehash['home'])
        # reverse list for breadcrumbs, where root is at front
        navdata = nodepath[::-1]
        return navdata


    def makenav_node_to_breadcrumb_html(self, nodelist, responsecontext):
        """Take a list of built node rows and return html for them."""
        # init
        html = ''
        labelproplist = ['label_short', 'label']
        # build nodehtmls
        for node in nodelist:
            nodehtml = self.makenav_node_to_html(node, {}, labelproplist, responsecontext)
            if (nodehtml != ''):
                html += nodehtml + '\n'
        # wrap in div class
        if (html != ''):
            html = '<div class="nav_breadcrumb">\n<ul>\n' + html + '</ul>\n</div> <!-- nav_breadcrumb -->'
        return html


























    def makenav_node_to_html(self, node, nodeproperties, labelproplist, responsecontext):
        """Return html for this node item."""
        import cgi
        html = ''

        # properties for the navbar menu
        isvisible = node.get_isvisible(responsecontext)
        if (not isvisible):
            return ''

        label = cgi.escape(node.get_label(labelproplist, responsecontext))
        url = node.get_menu_url(responsecontext)
        hint = node.get_menu_hint(responsecontext)


        #
        if (url!=None):
            url = cgi.escape(url)
            if (hint!=None):
                linkextra = 'TITLE="{0}"'.format(cgi.escape(hint))
            else:
                linkextra = ''
            html = '<a href="{0}" {1}>{2}</a>'.format(url,linkextra,label)
        else:
            html = label

        flag_isactive = misc.get_value_from_dict(nodeproperties,'flag_active',False)
        if (flag_isactive):
            html = '<span class="nav_active">' + html + '</span>'

        # wrap in div class
        html = '<li>' + html + '</li>'
        return html












class NavLink(object):
    """
    The NavLink class is a small helper class that is used to refer to a NavNode by id, with its own propertiess.
    It is used when we need to specify children NavNodes and we need to provide additional information.
    ATTN: TODO - this is not integrated into above functions of manager yet.
    """

    def __init__(self, id, properties={}):
        """Constructor for the clas."""
        self.id = id
        self.properties = properties


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""

        outstr = " "*indent + "Navlink '{0}' reporting in:\n".format(self.id)
        outstr += " "*indent + " properties: "+str(self.properties)
        #
        return outstr





















class NavNode(object):
    """
    The NavNode class represents a page on the site.
    """

    def __init__(self, id, properties={}):
        """Constructor for the clas."""
        self.id = id
        self.properties = properties
        self.resetbuild(None)



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "Navnode '{0}' reporting in:\n".format(self.id)
        outstr += " "*indent + " properties: {0}.\n".format(str(self.properties))
        outstr += " "*indent + " parents: {0}.\n".format(self.nodelist_tostring(self.parents))
        outstr += " "*indent + " children: {0}.\n".format(self.nodelist_tostring(self.children))
        if (self.route != None):
            outstr += " "*indent + " route: {0}.\n".format(self.route.id)
        return outstr


    def resetbuild(self, mewlosite):
        self.children = []
        self.parents = []
        self.route = None
        self.mewlosite = mewlosite



    def lookup_store_route(self):
        """Try to lookup or infer route reference."""
        routeid = self.get_property('route',None,False,None)
        if (routeid != None and not isinstance(routeid,basestring)):
            # they gave us a route object directly
            self.route = routeid
        else:
            # lookup by name
            if (routeid==None):
                routeid = self.id
            self.route = self.mewlosite.routemanager.lookup_route_byid(routeid)




    def get_property(self, propname, defaultval, flag_resolve, responsecontext):
        return self.get_propertyl([propname], defaultval, flag_resolve, responsecontext)

    def get_propertyl(self, propnames, defaultval, flag_resolve, responsecontext):
        for propname in propnames:
            if (propname in self.properties):
                val = self.properties[propname]
                if (flag_resolve):
                    # asked to resolve the value; check if it's a callable
                    if (hasattr(val, '__call__')):
                        return val(self, responsecontext)
                    return self.mewlosite.resolve(val)
                else:
                    return val
        return defaultval


    def nodelist_tostring(self, nodelist):
        if (len(nodelist)==0):
            return "none"
        namelist =  []
        for node in nodelist:
            namelist.append(node.id)
        nameliststring = ", ".join(namelist)
        return nameliststring




    def find_rootparent(self, rootnode = None):
        """Find the root parent of this node."""
        curnode = self
        while (True):
            if (len(curnode.parents)==0):
                break
            if (curnode == rootnode):
                break
            # ATTN: TODO - we only walk up single parent branch
            curnode = curnode.parents[0]
        return curnode






    def get_label(self, labelproplist, responsecontext):
        """Return value for menu/navbar creation."""
        val = self.get_propertyl(labelproplist,None,True,responsecontext)
        if (val==None):
            val=self.id
        # uppercase it
        val = val.upper()
        return val

    def get_menu_url(self, responsecontext):
        """Return value for menu/navbar creation."""
        val = self.get_propertyl(['url'], None, True, responsecontext)
        if (val==None):
            # no url specified in navnode, but perhaps we can construct it from the route associated with this navnode
            if (self.route != None):
                # ATTN: TODO - eventually we will need to pass context info to this function to account for url parameters, etc.
                val = self.route.construct_url()
        return val

    def get_menu_hint(self, responsecontext):
        """Return value for menu/navbar creation."""
        val = self.get_propertyl(['hint','help'], None, True, responsecontext)
        return val

    def get_isvisible(self, responsecontext):
        """Return value for menu/navbar creation."""
        val = self.get_property('visible', True, True, responsecontext)
        return val










