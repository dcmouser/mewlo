"""
loginhelper.py
This file contains helper code for login stuff
"""


# mewlo imports
from mewlo.mpackages.core.form.mform import MewloForm

# python imports

# addon imports
from forms.form_login import MewloForm_Login
from forms.form_register import MewloForm_Register




class LoginHelper(object):

    def __init__(self, request, response):
        self.request = request
        self.response = response
        #
        self.viewbasepath = '${addon_login_path}/views/'





    def renderpage_login(self):
        # set page info first (as it may be used in page contents)
        self.setpagecontext('login')
        # init form+formdata
        formdata = self.request.get_postdata()
        form = MewloForm_Login(formdata)

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            errordict = self.try_login(form.username, form.password)
            form.merge_errordict(errordict)
            # drop down and re-present form with errors

        # sessionid, as a test
        mewlosession = self.request.get_session()
        sessionid = mewlosession.hashkey

        # render form
        self.render_localview('login.jn2',{'form':form, 'sessionid': sessionid})
        # success
        return None



    def renderpage_register(self):
        # set page info first (as it may be used in page contents)
        self.setpagecontext('register')
        # init form+formdata
        formdata = self.request.get_postdata()
        form = MewloForm_Register(formdata)

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            errordict = self.try_register(form.username, form.password, form.email)
            form.merge_errordict(errordict)
            # drop down and re-present form with errors

        # render form
        self.render_localview('register.jn2',{'form':form})
        # success
        return None












    def renderpage_logout(self):
        # set page info first (as it may be used in page contents)
        self.setpagecontext('logout')

        # logout
        self.try_logout()

        # then page contents
        self.render_localview('logout.jn2')
        # success
        return None

























    def setpagecontext(self, pageid):
        """Helper function to set page id and context."""
        # ATTN: we should move this to a site-based method function which smarly settings pagecontext stuff
        # page id
        self.response.set_pageid(pageid)
        # page context
        self.response.add_pagecontext( {'isloggedin':True, 'username':'mouser'})



    def render_localview(self, viewfilepath, args={}):
        """Helper function to render relative view file."""
        self.response.render_from_template_file(self.viewbasepath+viewfilepath, args=args)





















    def try_logout(self):
        """Just log the user out, and redirect them somewhere."""
        #ATTN: unfinished
        return None







    def try_login(self, username, password):
        """Try logging in, return a dictionary of errors or REDIRECT if no error."""
        errordict = {}
        #ATTN: test
        errordict['password'] = "Password is incorrect."
        return errordict






    def try_register(self, username, password, email):
        """Try registering user, return a dictionary of errors or REDIRECT if no error."""
        errordict = {}
        #ATTN: test
        errordict[MewloForm.DEF_GenericErrorKey] = "Registration is currently closed."
        return errordict



