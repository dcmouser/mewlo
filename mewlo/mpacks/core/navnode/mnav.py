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
        Note that eventually we may want any property here to be able to be specified as an ajax function; this allows us to do lazy evaluation of dynamic stuff


ATTN: There are some aspects of the current implementation that are unpleasant:
As it stands now, the site has a NavNodeManager which is a collection of NavNodes.
NavNodes themselves contain properties which may involve lambdas and aliases that resolve differently for each request (such as showing user name on logout menu item).
So when we build a menu for a user's request, we will dynamically resolve some of these NavNode properties, and cache this information local to the request.
This is a bit messy as we would really like to carry around such information annotated onto the NavNodes themselves, but that isn't feasible since they are shared among requests.
It's also an issue because we may have several functions invoked from the view templates that make use of the same NavNodes (for example breadcrumbs and menus)
and we would prefer not to have to resolve properties twice on the same request.  Solving this means caching results of resolving properties and storing local to the response object.

For now I have implemented a messy caching system that caches resolved navnode properties in the response context object (which also holds information about the current navnode pageid, etc).
This isn't such a bad solution in theory, as it makes it possible for us to both add a per-request annotated properties to nodes (like indicating which nodes are on the active path),
as well as letting us cache node dynamic values (like dynamic titles and visibility computations) so that we only have to do it once even if using multiple menus (breadcrumbs, etc.).

However, it uses a very inefficient looking deep dictionary lookup like (context['nodes']['nodeid']['propertyname']) and i worry about the cost of this, as well as the polution to responsecontext.
A reasonable solution might be to use a special data structure for cached note properties, and perhaps assign navnodes a unique numeric counter id at startup, and index by that.

Another thing we do is allow nodes to specify a list of parents and/or children by nodename.  This lets one create a hierarchy dynamically and add to it from wherever you want.

Controllers should set the current page id and other context available to navigation nodes using the reponse.add_rendercontext() function, e.g.     response.add_rendercontext('contact', {'isloggedin':True, 'username':'mouser'} )

ATTN: 1/28/14
The last time i looked at this code i got confused by the use of responsecontext.
responsecontext is a dict that serves two purposes -- first it is available for use by lambda functions which can look at request/response/user
second, it can be written to under key 'navnodecache' which is itself a MThinDict, in order to cache the results of values (lambda functions) for nodes so that we don't have to recompute them multiple times while traversing tree.
Note that this cache starts off blank on each request.
"""


# mewlo imports
from ..helpers import misc
from ..manager import manager

# python imports




class NavNodeManager(manager.MewloManager):
    """
    The NavNodeManager class manages a collection of NavNodes.
    The most common usage would be that each site has a NavNodeManager to represent the site hierarchy
    """

    # class constants
    description = "Manages the navnode structures that build site maps and menus and breadcrumbs"
    typestr = "core"


    # class constants
    DEF_navnodecache_keyname = 'navnodecache'


    def __init__(self, mewlosite, debugmode):
        """Constructor for the clas."""
        super(NavNodeManager,self).__init__(mewlosite, debugmode)
        self.nodes = []
        self.nodehash = {}


    def startup(self, eventlist):
        """Called at start of application."""
        super(NavNodeManager,self).startup(eventlist)
        # initial nodes
        self.sitenode = NavNode('site')
        self.orphannode = NavNode('__orphans__')
        startnodes = [self.sitenode, self.orphannode]
        self.add_nodes(startnodes)


    def poststartup(self, eventlist):
        """Called after all managers finish with startup()."""
        super(NavNodeManager,self).poststartup(eventlist)
        #
        self.buildstructure()



    def shutdown(self):
        """Called at shutdown of application."""
        super(NavNodeManager,self).shutdown()




    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""

        outstr = " "*indent + "NavNodeManager reporting in with {0} nodes:\n".format(len(self.nodes))
        outstr += self.dumps_description(indent+1)
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
            #print "ATTN: debug building navnode structure with node {0} having parents {1}.".format(node.id,str(parents))
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
            else:
                raise Exception("Could not find navnode with id '{0}'.".format(nodeid))
        return nodelist










    def find_current_and_root(self, rootnode, responsecontext):
        """Given response and a possible explicit rootnode, find current node and rootnode to use."""
        currentnodeid = responsecontext.get_value('pagenodeid')
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


    # actve row helpers


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

        # build rows, walk from parent down to next to last item (dont do currentnode)
        rows = []
        nodecount = len(nodepath)
        for i in range(nodecount-1,-1,-1):
            # the parent of this row
            parentnode = nodepath[i]
            # the active child on this row
            if (i==0):
                activechildnode = None
            else:
                activechildnode = nodepath[i-1]
            # make the row
            row = self.makenav_activerowlist_onerow(parentnode, activechildnode, responsecontext)
            # if we got any noded, sort and then add them
            if (len(row)>0):
                # sort the row
                row = self.sort_nodelist_byproperty(row, responsecontext, False, ['sortweight'],0.0)
                rows.append(row)

        # return it
        navdata = rows
        return navdata



    def makenav_activerowlist_onerow(self, parentnode, activechildnode, responsecontext):
        """Make a list (row) of nodes, using children of parent node, and marking the activechildnode as active."""
        row = []
        children = parentnode.children
        for child in children:
            if (child == activechildnode):
                # annotate with the flag_active setting for this navnode for this request
                child.set_response_property('flag_active',True,responsecontext)
            row.append(child)
        return row



    def sort_nodelist_byproperty(self, nodelist, responsecontext, flag_isalpha, propnames, defaultval):
        """Given a nodelist, return sorted version, sorted by node numeric propertyname (with a default value if missing).
        """
        if (flag_isalpha):
            newnodelist = sorted(nodelist, key = lambda node: (node.get_propertyl(propnames, defaultval, True, responsecontext)).lower())
        else:
            newnodelist = sorted(nodelist, key = lambda node: node.get_propertyl(propnames, defaultval, True, responsecontext))
        return newnodelist





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
        labelproplist = ['menulabel']
        for node in row:
            nodehtml = self.makenav_node_to_html(node, labelproplist, responsecontext)
            html += nodehtml
        # wrap in div class
        if (html != ''):
            html = '<div class="nav_bar_row">\n<ul>\n' + html + '\n</ul>\n</div> <!-- nav_bar_row -->'
        return html









    # breadcrumb helpers


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
        # ATTN: this is a bit kludgey
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
        labelproplist = ['menulabel_short', 'menulabel']
        # build nodehtmls
        for node in nodelist:
            nodehtml = self.makenav_node_to_html(node, labelproplist, responsecontext, ['visible_breadcrumb','visible'])
            if (nodehtml != ''):
                html += nodehtml + '\n'
        # wrap in div class
        if (html != ''):
            html = '<div class="nav_breadcrumb">\n<ul>\n' + html + '</ul>\n</div> <!-- nav_breadcrumb -->'
        return html

























    # generic navnode html helper



    def makenav_node_to_html(self, node, labelproplist, responsecontext, visiblefieldlist = ['visible']):
        """Return html for this node item."""
        import cgi
        html = ''

        # if its not visible, we can stop right now
        isvisible = node.get_isvisible(responsecontext, visiblefieldlist)
        if (not isvisible):
            return ''

        # other properties
        label = cgi.escape(node.get_label(labelproplist, responsecontext))
        url = node.get_menu_url(responsecontext)
        hint = node.get_menu_hint(responsecontext)
        flag_linkurl = node.get_flag_linkurl(responsecontext)

        # build main html
        if (url!=None and flag_linkurl):
            url = cgi.escape(url)
            if (hint!=None):
                linkextra = 'TITLE="{0}"'.format(cgi.escape(hint))
            else:
                linkextra = ''
            html = '<a href="{0}" {1}>{2}</a>'.format(url,linkextra,label)
        else:
            html = label

        # active highlighting
        flag_isactive = node.isactive(responsecontext)
        if (flag_isactive):
            html = '<span class="nav_active">' + html + '</span>'

        # wrap in div class
        html = '<li>' + html + '</li>'
        return html
















    def calcnav_currentpage_title(self, responsecontext):
        """
        Return title of current page from current navnode
        """
        # init
        # get currentnode and rootnode to use
        (currentnode, rootnode) = self.find_current_and_root(None, responsecontext)
        # if nothing to do, return now
        if (currentnode == None):
            # unknown pagetitle
            return ''
        return currentnode.get_pagetitle(responsecontext)

























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
        """Constructor for the class."""
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
        # copy id to property for uniform access
        self.properties['id']=self.id



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
            self.route = self.mewlosite.comp('routemanager').lookup_route_byid(routeid)




    def get_property(self, propname, defaultval, flag_resolve, responsecontext):
        return self.get_propertyl([propname], defaultval, flag_resolve, responsecontext)

    def get_propertyl(self, propnames, defaultval, flag_resolve, responsecontext):
        #print "ATTN: in get_propertyl {0} with context = {1}".format(str(propnames),str(responsecontext))
        for propname in propnames:
            if (responsecontext != None):
                # check for a cached value
                val = self.get_response_property(propname, responsecontext, None)
                if (val != None):
                    # we found a cached value, return it
                    #print "ATTN: USING CACHED VALUE FOR PROP {0} of node {1} value is {2}.".format(propname,self.id,val)
                    return val
            if (propname in self.properties):
                val = self.properties[propname]
                if (flag_resolve):
                    # asked to resolve the value, see if it resolved differently and check if it's a callable
                    if (hasattr(val, '__call__')):
                        # it's a callable (lambda)
                        computedval = val(self, responsecontext)
                    else:
                        # let's see if it needs resolving
                        computedval = self.mewlosite.resolve(val)
                    # is the computed value different?
                    if (computedval != val):
                        val = computedval
                    # cache it before returning
                    self.set_response_property(propname, val, responsecontext)
                # return found value
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



    def get_pagetitle(self, responsecontext):
        """Return value for menu/navbar creation."""
        val = self.get_propertyl(['pagetitle','menulabel','menulabel_short'],None,True,responsecontext)
        if (val==None):
            val=self.id
        return val


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
                val = self.route.construct_url(flag_relative=True)
        else:
            # val is the url, but we need to add site prefix
            val = self.relative_url(val)
        return val

    def get_menu_hint(self, responsecontext):
        """Return value for menu/navbar creation."""
        val = self.get_propertyl(['menuhint','menuhelp'], None, True, responsecontext)
        return val

    def get_isvisible(self, responsecontext, visiblefieldlist = ['visible']):
        """Return value for menu/navbar creation."""
        val = self.get_propertyl(visiblefieldlist, True, True, responsecontext)
        return val

    def get_flag_linkurl(self, responsecontext):
        val = self.get_propertyl(['flag_linkurl'], True, True, responsecontext)
        return val


    def isactive(self,responsecontext):
        return self.get_property('flag_active', False, True, responsecontext)



    def set_response_property(self, propertyname, value, responsecontext):
        """Set a 'cached' value in response context for this node."""
        keyname = self.id + '_' + propertyname
        responsecontext[NavNodeManager.DEF_navnodecache_keyname][keyname] = value

    def get_response_property(self, propertyname, responsecontext, defaultval):
        """Get a 'cached' value in response context for this node."""
        if (responsecontext == None):
            return defaultval
        keyname = self.id + '_' + propertyname
        return responsecontext.get_subvalue(NavNodeManager.DEF_navnodecache_keyname,keyname, defaultval)




    def relative_url(self, url):
        """Ask site to construct proper relative url on the site by adding site prefix."""
        return self.mewlosite.relative_url(url)


