"""
loginhelper.py
This file contains helper code for login stuff
"""


# mewlo imports


# python imports





class LoginHelper(object):

    def __init__(self, request, response):
        self.request = request
        self.response = response
        #
        self.viewbasepath = '${addon_login_path}/views/'





    def renderpage_login(self):
        # set page info first (as it may be used in page contents)
        self.setpagecontext('login')
        # render page content
        self.render_localview('login.jn2')
        # success
        return None



    def renderpage_logout(self):
        # set page info first (as it may be used in page contents)
        self.setpagecontext('logout')
        # then page contents
        self.render_localview('logout.jn2')
        # success
        return None



    def renderpage_register(self):
        # set page info first (as it may be used in page contents)
        self.setpagecontext('register')
        # then page contents
        self.render_localview('register.jn2')
        # success
        return None





















    def setpagecontext(self, pageid):
        """Helper function to set page id and context."""
        # page id
        self.response.set_pageid(pageid)
        # page context
        self.response.add_pagecontext( {'isloggedin':True, 'username':'mouser'})



    def render_localview(self, viewfilepath):
        """Helper function to render relative view file."""
        self.response.render_from_template_file(self.viewbasepath+viewfilepath)



