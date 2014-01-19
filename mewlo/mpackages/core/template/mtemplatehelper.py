"""
mtemplatehelper.py
This module contains classes and functions that are passed to template to assist in producing text (menus, navbars, etc.)
The template files can refer to and make calls of this class [see testsite1/views/heeader.jn2 which makes calls like {{ thelper.nav_bar_html(response) }} ]
"""

# mewlo imports
from ..manager import manager

# python imports
import os.path







class MewloTemplateHelper(manager.MewloManager):
    """The MewloTemplateHelper class helps templates render output."""

    def __init__(self):
        super(MewloTemplateHelper,self).__init__()

    def startup(self, mewlosite, eventlist):
        super(MewloTemplateHelper,self).startup(mewlosite,eventlist)

    def shutdown(self):
        super(MewloTemplateHelper,self).shutdown()






    def make_templateargs(self, inargs, request, response):
        """Add default args to expose information and provide args that the template can use."""
        templateargs = inargs.copy()
        # make data available to temlate (these are available at root level
        templateargs['response'] = response
        templateargs['request'] = request
        templateargs['thelper'] = self
        templateargs['site'] = request.mewlosite
        # we could also add all site aliases/resolving to root level
        resolvedaliases = request.mewlosite.assetmanager.get_resolvedaliases()
        templateargs['alias'] = resolvedaliases
        return templateargs




    def nav_bar_html(self, response):
        """Make a navar html."""
        # get response context
        responsecontext = response.context
        # build list of rows
        activebars = self.mewlosite.navnodes.makenav_activerowlist(responsecontext)
        # now convert to html
        html = self.mewlosite.navnodes.makenav_rowlist_to_html(activebars,responsecontext)
        return html


    def nav_breadcrumb_html(self, response):
        """Make a navar html."""
        # get response context
        responsecontext = response.context
        # build list of rows
        nodelist = self.mewlosite.navnodes.makenav_breadcrumb_list(responsecontext)
        # now convert to html
        html = self.mewlosite.navnodes.makenav_node_to_breadcrumb_html(nodelist,responsecontext)
        return html


    def nav_pagetitle(self, response):
        """Page title from navnodes."""
        # get response context
        responsecontext = response.context
        return self.mewlosite.navnodes.calcnav_currentpage_title(responsecontext)




    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloTemplateHelper (" + self.__class__.__name__ + ") reporting in.\n"
        return outstr
