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

    # class constants
    description = "The template helper is accessed within view files to provide shortcut helper functions and text"
    typestr = "core"


    def __init__(self, mewlosite, debugmode):
        super(MewloTemplateHelper,self).__init__(mewlosite, debugmode)






    def nav_bar_html(self, response):
        """Make a navar html."""
        # get response context
        responsecontext = response.get_rendercontext()
        # build list of rows
        activebars = self.mewlosite.comp('navnodemanager').makenav_activerowlist(responsecontext)
        if (len(activebars) == 0):
            html = 'ERROR: PAGENODEID {0} COULD NOT BE LOCATED; NO NAVIGATION BAR GENERATED.'.format(responsecontext.get_value('pagenodeid','PAGENODEID_NOT_SET'))
        else:
            # now convert to html
            html = self.mewlosite.comp('navnodemanager').makenav_rowlist_to_html(activebars,responsecontext)
        return html


    def nav_breadcrumb_html(self, response):
        """Make a navar html."""
        # get response context
        responsecontext = response.get_rendercontext()
        # build list of rows
        nodelist = self.mewlosite.comp('navnodemanager').makenav_breadcrumb_list(responsecontext)
        if (len(nodelist) == 0):
            html = 'ERROR: PAGENODEID {0} COULD NOT BE LOCATED; NO BREADCRUMB BAR GENERATED.'.format(responsecontext.get_value('pagenodeid','PAGENODEID_NOT_SET'))
        else:
            # now convert to html
            html = self.mewlosite.comp('navnodemanager').makenav_node_to_breadcrumb_html(nodelist,responsecontext)
        return html


    def nav_pagetitle(self, response):
        """Page title from navnodes."""
        # get response context
        responsecontext = response.get_rendercontext()
        return self.mewlosite.comp('navnodemanager').calcnav_currentpage_title(responsecontext)












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
        reth = ''
        # skip hidden fields
        if (field.type=='HiddenField'):
            return field()
        css_class = ''
        #
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
            user = session.get_user()
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
        outstr += self.dumps_description(indent+1)
        return outstr






















    def session_messages_html(self, request, title=None):
        """Show any pending session messages for client."""
        messages = request.get_sessionmessages(flag_consume=True)
        if (not messages):
            return ''
        return self.messages_html(messages, title)



    def page_messages_html(self, request, title=''):
        """Show any page messages for client -- these are generic messages that can be added to any page context"""
        messages = request.get_pagemessages()
        if (not messages):
            return ''
        return self.messages_html(messages, title)



    def messages_html(self, messages, title):
        """Format some messages."""
        if (not messages):
            return ''
        reth = ''
        reth += '\n<div class="messagelist">\n'
        if (title):
            reth += '<h2>{0}</h2>\n'.format(title)
        reth += '<ul>\n'
        #
        for messagedict in messages:
            if (('cls' in messagedict) and (messagedict['cls'])):
                classpart = 'class="messageclass_{0}"'.format(messagedict['cls'])
            else:
                classpart = ''
            reth += '<li {0}>{1}</li>\n'.format(classpart, messagedict['msg'])
        #
        reth += '</ul>\n'
        reth += '</div> <!-- messagelist -->\n'
        return reth
