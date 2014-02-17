"""
accounthelper.py
This file contains helper code for account login and registration tyoe stuff
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm
from mewlo.mpacks.core.user import muser, musermanager

# python imports

# addon imports
from forms.form_login import MewloForm_Login
from forms.form_register_justemail import MewloForm_Register_JustEmail
from forms.form_register_usernamepassemail import MewloForm_Register_UsernamePasswordEmail




class AccountHelper(object):

    def __init__(self, request, response):
        self.request = request
        self.response = response
        #
        self.viewbasepath = '${addon_account_path}/views/'
        #
        # we all of our non-form view files here, so that they are in one place
        # the forms specify their own view files
        self.viewfiles = {
            'regcomplete': 'register_complete.jn2',
            'logincomplete': 'login_complete.jn2',
            'logout': 'logout.jn2',
            }



    def sitecomp_usermanager(self):
        return self.request.mewlosite.comp('usermanager')


    def renderpage_login(self):
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('login')
        # init form+formdata
        formdata = self.request.get_postdata()
        form = MewloForm_Login(formdata)

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            errordict = self.try_login(form.username.data, form.password.data)
            if ((errordict == None) or (len(errordict)==0)):
                # all good
                self.render_localview(self.viewfiles['logincomplete'])
                # success
                return None
            # drop down and re-present form with errors
            form.merge_errordict(errordict)

        # render form
        self.render_localview(form.get_viewfilename(),{'form':form})
        # success
        return None



    def renderpage_register(self):
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('register')
        # init form+formdata
        formdata = self.request.get_postdata()
        form = MewloForm_Register_UsernamePasswordEmail(formdata)

        # If we want we can remove form fields here like so:
        #delattr(form, 'accept_rules')

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            errordict = self.try_register(form.username.data, form.password.data, form.email.data)
            if ((errordict == None) or (len(errordict)==0)):
                # success
                # render form
                self.render_localview(self.viewfiles['regcomplete'])
                # success
                return None
            else:
                form.merge_errordict(errordict)
                # drop down and re-present form with errors

        # render form
        self.render_localview(form.get_viewfilename(),{'form':form})
        # success
        return None












    def renderpage_logout(self):
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('logout')

        # logout
        self.try_logout()

        # then page contents
        self.render_localview(self.viewfiles['logout'])
        # success
        return None

























    def set_renderpageid(self, pageid):
        """Helper function to set page id."""
        self.response.set_renderpageid(pageid)




    def render_localview(self, viewfilepath, args=None):
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
        user, errordict = self.sitecomp_usermanager().login_user(username=username, password_plaintext=password_plaintext)
        if (user != None):
            # ok it's a success, user was created.
            # tell the session about the user's identity
            self.request.set_user(user)
        return errordict






    def try_register(self, username, password_plaintext, email):
        """Try registering user, return a dictionary of errors or REDIRECT if no error."""
        #ATTN: test
        user, errordict = self.sitecomp_usermanager().create_user(username=username, password_plaintext=password_plaintext, email=email)
        if (user != None):
            # ok it's a success, user was created.
            # tell the session about the user's identity
            self.request.set_user(user)
        return errordict



