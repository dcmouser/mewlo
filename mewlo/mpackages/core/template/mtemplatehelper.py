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












    def html_autoform(self, form):
        """Render form html automatically by inspecting form fields."""
        reth = ''
        reth += '<form method="POST">\n'
        # generic error?
        genericerrorstr = form.get_genericerrorstr()
        if (genericerrorstr != None):
            reth += '<div class="form_errors_generic">There are errors on this form: ' + genericerrorstr + '</div><br/>\n'
        #
        for field in form:
            reth += self.html_formfield_witherror(field)
        #
        reth += '<br/>\n'
        reth += '<input type="submit"/>\n';
        reth += '</form>\n';
        #
        return reth




    def html_formfield_witherror(self, field):
        """Return html for the form with inline errors."""
        #
        css_class = ''
        #
        reth = ''
        reth += '<div class="form_field">\n'
        # label
        reth += str(field.label) + ': '
        # field with errors
        if (field.errors):
            # if it's got an error, set the field class so we can render it differently
            css_class = 'has_error'
            reth += field(class_=css_class)+'\n'
            reth += '<ul class="form_errors">\n'
            for error in field.errors:
                reth += '<li>{0}</li>\n'.format(error)
            reth += '</ul>\n'
        else:
            reth += field()+'\n'
        reth += '</div>\n'
        #
        return reth




    def html_debugfooter(self, request):
        """Some simple debug html at bottom of page."""
        session = request.get_session(False)
        if (session != None):
            user = session.get_user(False)
            if (user != None):
                username = user.username
            else:
                username = 'anonymous'
            reth = "[ Sessionid: {0} | User: {1} ]".format(session.hashkey,username)
        else:
            reth = "[no session created for this request]"
        return reth








    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloTemplateHelper (" + self.__class__.__name__ + ") reporting in.\n"
        return outstr
