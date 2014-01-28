"""
loginhelper.py
This file contains helper code for login stuff
"""


# mewlo imports
from mewlo.mpackages.core.form.mform import MewloForm
from mewlo.mpackages.core.user import muser

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
            errordict = self.try_login(form.username.data, form.password.data)
            if ((errordict == None) or (len(errordict)==0)):
                # all good
                self.render_localview('loggedin.jn2')
                # success
                return None
            # drop down and re-present form with errors
            form.merge_errordict(errordict)

        # render form
        self.render_localview('login.jn2',{'form':form})
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
            errordict = self.try_register(form.username.data, form.password.data, form.email.data)
            if ((errordict == None) or (len(errordict)==0)):
                # success
                # render form
                self.render_localview('register_complete.jn2')
                # success
                return None
            else:
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
        # test
        user = self.request.get_user(False)
        if (user == None):
            print "Request is from anonymous guest user."
        else:
            print "Request is from user: '{0}'.".format(str(user.username))
        # page context
        self.response.add_pagecontext( {'isloggedin':True, 'username':'mouser'})



    def render_localview(self, viewfilepath, args={}):
        """Helper function to render relative view file."""
        self.response.render_from_template_file(self.viewbasepath+viewfilepath, args=args)





















    def try_logout(self):
        """Just log the user out, and redirect them somewhere."""
        # set session user to None
        self.request.set_user(None)
        return None







    def try_login(self, username, password_plaintext):
        """Try logging in, return a dictionary of errors or REDIRECT if no error."""
        errordict = {}
        #ATTN: test
        user, errordict = muser.MewloUser.login_user(username=username, password_plaintext=password_plaintext)
        if (user != None):
            # ok it's a success, user was created.
            # tell the session about the user's identity
            self.request.set_user(user)
        return errordict






    def try_register(self, username, password_plaintext, email):
        """Try registering user, return a dictionary of errors or REDIRECT if no error."""
        #ATTN: test
        user, errordict = muser.MewloUser.create_user(username=username, password_plaintext=password_plaintext, email=email)
        if (user != None):
            # ok it's a success, user was created.
            # tell the session about the user's identity
            self.request.set_user(user)
        return errordict



