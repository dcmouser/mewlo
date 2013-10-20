"""
mtemplatehelper.py
This module contains classes and functions that are passed to template to assist in producing text (menus, navbars, etc.)
"""


# python imports
import os.path







class MewloTemplateHelper(object):
    """The MewloTemplateHelper class helps templates render output."""

    def __init__(self):
        self.mewlosite = None

    def startup(self, mewlosite, eventlist):
        self.mewlosite = mewlosite

    def shutdown(self):
        pass


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





    def navbar(self, response):

        # build list of rows
        activebars = self.mewlosite.navnodes.makenav_activerowlist(response)
        # now convert to html
        navbarhtml = self.mewlosite.navnodes.makenav_rowlist_to_html(activebars,response)
        #
        return navbarhtml





    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloTemplateHelper (" + self.__class__.__name__ + ") reporting in.\n"
        return outstr
