"""
accounthelper.py
This file contains helper code for account login and registration tyoe stuff
"""


# mewlo imports
from mewlo.mpacks.core.form.mform import MewloForm
from mewlo.mpacks.core.user import muser, musermanager
from mewlo.mpacks.core.reqresp.mrequesthelper import  MewloRequestHandlerHelper
from mewlo.mpacks.core.eventlog.mevent import EFailure, EException

# python imports

# addon imports
from forms.form_login import MewloForm_Login
from forms.form_register_immediate import MewloForm_Register_Immediate
from forms.form_register_deferred import MewloForm_Register_Deferred
from forms.form_register_deferred_finalize import MewloForm_Register_Deferred_Finalize





class AccountHelper(MewloRequestHandlerHelper):
        
    # class constants
    DEF_VFTYPE_pre_user_verification = 'VFTYPE_pre_user_verification'



    def __init__(self, request, response):
        # call parent constructor
        super(AccountHelper, self).__init__(request, response)
        #
        self.viewbasepath = '${addon_account_path}/views/'
        #
        # we all of our non-form view files here, so that they are in one place (the forms themselves can specify their own default view files -- see form.get_viewfilename())
        self.viewfiles = {
            'login_complete': 'login_complete.jn2',
            'logout_complete': 'logout_complete.jn2',
            'register_done_immediate': 'register_complete_immediate.jn2',
            'register_done_deferred_verification': 'register_done_deferred_verification.jn2',
            'register_done_deferred_usercreated': 'register_done_deferred_usercreated.jn2',            
            'verify_registration_deferred_error_codenotfound': 'verify_registration_deferred_error_codenotfound.jn2',
            'verify_registration_deferred_error_emailinuse': 'verify_registration_deferred_error_emailinuse.jn2',         
            'register_deferred_email_verificationsent': 'register_deferred_email_verificationsent.jn2',
            }

































    
    

    def handlepage_login(self):
        """Present and consume the login form.
        Return failure"""
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('login')
        # init form+formdata
        formdata = self.request.get_postdata()
        # the form we will use
        form = MewloForm_Login(formdata)

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            # build dictionary of parameters of registration
            userdict = form.data
            # now try logging in
            errordict = self.try_login(userdict)
            if (not dict):
                # all good
                self.render_localview(self.viewfiles['login_complete'])
                # success
                return None
            # drop down and re-present form with errors
            form.merge_errordict(errordict)

        # render form (use forms default view)
        self.render_localview(form.get_viewfilename(),{'form':form})
        # success
        return None



    def try_login(self, userdict):
        """Try logging in, return a dictionary of errors or REDIRECT if no error.
        Return error dictionary."""

        # try to log in the user
        user, errordict = self.sitecomp_usermanager().login_user(userdict)
        if (user != None):
            # ok it's a success, user was found and loaded.
            # tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
            self.request.set_user(user)
        # return success or error
        return errordict






















    def handlepage_logout(self):
        """Present and consume the logour form.
        Return failure."""
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('logout')
        # logout
        self.try_logout()
        # then page contents
        self.render_localview(self.viewfiles['logout_complete'])
        # success
        return None



    def try_logout(self):
        """Just log the user out, and redirect them somewhere.
        Return failure"""
        # set session user to None (note they still keep their session, but it no longer has a user associated with it)
        self.request.clearloggedinuser()
        # success
        return None


































































    def handlepage_register_immediate(self):
        """Handle immediate registration case."""
        formclass = MewloForm_Register_Immediate
        return self.do_handlepage_register(formclass, flag_immediate = True)

    
    def handlepage_register_deferred(self):
        """Handle deferred registration case."""
        formclass = MewloForm_Register_Deferred      
        return self.do_handlepage_register(formclass, flag_immediate = False)







    def do_handlepage_register(self, formclass, flag_immediate):
        """Handle registration based on the formclass and type of registration."""
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('register')
        # init form+formdata
        formdata = self.request.get_postdata()
        # the form to be used
        form = formclass(formdata)
       
        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            userdict = form.data
            # now try to register them
            errordict, successmessage = self.try_register(userdict, flag_immediate)
            if (not errordict):
                # success; called function will have handled rendering view, so we are now done and do not want to drop down
                return None
            else:
                # add errors to form
                form.merge_errordict(errordict)
                # drop down and re-present form with errors

        # render form
        self.render_localview(form.get_viewfilename(), {'form':form})
        # success
        return None















    def try_register(self, userdict, flag_immediate):
        """Try registering user.  On success, *WE* display success page.
        Return tupe (errordict, successmessage)."""

        # first let's see if we can find an existing user with this unique info -- if so, it's an error
        errordict = self.sitecomp_usermanager().error_if_user_exists(userdict)
        if (errordict):
            return errordict, ''

        # create the user instantly or defer via verification
        if (flag_immediate):
            # create user instantly
            (user, errordict, successmessage) = self.create_newuser(userdict)
            if (user != None):
                # a user was created; tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
                self.request.set_user(user)
            success_viewfile = self.viewfiles['register_done_immediate']
        else:
            # deferrred user creation, we create a verification instead
            (verification, errordict, successmessage) = self.precreate_newuser_deferred_justverification(self.request, userdict)
            success_viewfile = self.viewfiles['register_done_deferred_verification']          

        if (not errordict):
            # success, we handle rendering page
            self.render_localview(success_viewfile, {'successmessage': successmessage})

        # return
        return (errordict, successmessage)
















    def create_newuser(self, userdict, verifiedfields=[]):
        """Create a new user right away.  Send them an email verification link after."""
        (user, errordict, successmessage) = self.sitecomp_usermanager().create_user(userdict, verifiedfields=verifiedfields)
        return (user, errordict, successmessage)









    def precreate_newuser_deferred_justverification(self, request, userdict):
        """
        Create a verification entry for a new user registration.
        We take a userdict instead of explicit variables for username, email, password, so that we can eventually accomodate whatever initial user properties we have specified at time of registration.
        return tuple (verification, errordict, successmessage); if there are errors return them and userobject as None
        """

        # first let's see if we can find the user
        errordict = self.sitecomp_usermanager().error_if_user_exists(userdict)
        if (errordict):
            return (None, errordict, '')

        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()

        # ok so now we want to create (and email the user) a verification entry that they can use to confirm and create this account

        # verification properties
        # ATTN:TODO - move some of this stuff to options and constants
        verification_type = self.DEF_VFTYPE_pre_user_verification
        # set verification_varname for quick lookup
        verification_varname = 'email'
        verification_varval = userdict['email']
        # other values
        is_shortcode = False
        expiration_days = 14
        # the verification fields will contain the userdict so we can reinstate any values they provided at sign up time, when they confirm
        extradict = {'userdict':userdict}

        # before we create a new verification entry, we *may* sometimes want to delete/invalidate previous verification requests of same type from same user/session
        # note that we do NOT want to delete previous verifications just because they were sent to this same email address if the sessions were different
        verificationmanager.invalidate_previousverifications(verification_type, request)
        # create it via verificationmanager
        verification = verificationmanager.create_verification(verification_type)
        # set it's properties
        verification.init_values(request, expiration_days, verification_varname, verification_varval, extradict, is_shortcode)
        # save it
        verification.save()
        
        # now send them an email telling them how to verify
        emailtemplatefile = self.calc_localtemplatepath(self.viewfiles['register_deferred_email_verificationsent'])
        verificationurl = self.calc_verificationurl_registration_deferred(verification)
        maildict = {
            'to': [ userdict['email'] ],
            'subject': u'Signup verification email',
            'body': self.get_mewlosite().renderstr_from_template_file(emailtemplatefile, {'verificationurl':verificationurl})
        }
        failure = self.sitecomp_mailmanager().send_email(maildict)
        if (failure != None):
            # failure sending email gets added to errordict at root ('') rather than related to a specific field
            errordict[''] = str(failure)
        
        # message to be displayed to user (note: this is only used if errordict is empty)
        successmessage = 'Your account has been registered, but your email must be verified before you can login.  Check your email for your verification code.'
        
        # return
        return (verification, errordict, successmessage)





    
    def calc_verificationurl_registration_deferred(self, verification):
        """Compute the verification url for a verification object for deferred registration.
        This will require asking the site what the base url should be.
        """
        url = self.get_mewlosite().build_routeurl_byid('register_deferred_verify', flag_relative=False, args={'code':verification.verification_code} )
        return url

















































































    def handlepage_verify_registration_deferred(self):
        """Client visits deferred registration verification page."""
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('register_deferred_verify')
        self.try_verify_registration_deferred()
        # success
        return None




    def try_verify_registration_deferred(self):
        """Try to complete their verification."""
        # get code from args
        args = self.request.get_route_parsedargs()
        verification_code = args['code']
        # try to register -- caller will handle rendering the result
        return self.try_verify_registration_deferred_withcode(verification_code)






    def try_verify_registration_deferred_withcode(self, verification_code):
        """Try to complete their deferred verification given a code."""

        # look up the code
        verification, failure = self.verify_registration_validatecode(verification_code)
        if (failure != None):
            # ATTN: TODO - make this a form where they can provide the verification code manually
            self.render_localview(self.viewfiles['verify_registration_deferred_error_codenotfound'], {'failure':failure})
            return

        # code is good.       
        # in a classic site signup, we would have created the user object already, and registration "verification" would only be about proving their already-guaranteed unique email address
        # but we are allowing for some more interesting scenarios, where in the meantime after they initially registered:
        # 1. we have gathered information from them about their DESIRED username and password, but we haven't actually created their account yet
        # 2. or we haven't even asked them anything other than their desired email.
        # 3. furthermore, all of these values, INCLUDING their email (which they have now proved) may actually be already used by another real user that signed up while they were waiting to verify, so we must force them to change it
        # 4. if they specified a now-inuse username at registration, we can let them change it now; if they specified a now-inuse email, we need to make them start over
        
        # a first thing that might make sense is to check if a user exist with their email that they just verified; if so, we need to give them the bad news and make them re-register
        # varname and varval should be email and email address that we are verifiying
        checkuserdict = {verification.verification_varname: verification.verification_varval}
        errordict = self.sitecomp_usermanager().error_if_user_exists(checkuserdict)
        if (errordict):
            # another user has this email, sorry sucker, you took too long to verify
            self.render_localview(self.viewfiles['verify_registration_deferred_error_emailinuse'], {'failure':failure})
            return

        # ok email is still available, now we'd like to present them with a form that contains:
        # 1. the verification code as hidden var
        # 2. any pre-specified user profile values that they filled in during initial registration that we want to let them modify at this point
        # 3. their pre-specified email, fixed+disabled
        # 4. any additional other profile fields we want from them at this stage
        # only when they submit this successfully do we actually consume the verification entry and create their account
        
        # caller will handle rendering any page results
        return self.try_finalize_registration_deferred_withverification(verification)
    
    







    def verify_registration_validatecode(self, verification_code):
        """Locate verification, check it for different kinds of errors.
        return tuple (verification, failure).
        """
        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()        
        
        # find verification entry
        verification = verificationmanager.find_bylongcode(verification_code)
        
        # then check it
        verification_type_expected = self.DEF_VFTYPE_pre_user_verification
        is_shortcode_expected = False
        failure = verificationmanager.basic_validation(verification, verification_code, self.request, verification_type_expected, is_shortcode_expected)
        # return success or failure
        return verification, failure
    
    
    
    
    
    
    
    
    def try_finalize_registration_deferred_withverification(self, verification):
        """
        They have provided a valid registration code which we matched to a verification entry; now we will let them fill in the final form to create their account.
        See try_verify_registration_deferred_withcode for more info.
        """
        
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('register_deferred_verify')
        # init form+formdata
        formdata = self.request.get_postdata()
        # form to be used
        form = MewloForm_Register_Deferred_Finalize(formdata)

        # default viewfilename
        viewfilename = form.get_viewfilename()
        viewargs = {'form':form}

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            userdict = form.data
            # now try to register them
            user, errordict, successmessage = self.create_newuser_deferred(userdict)
            if (not errordict):
                # success
                viewfilename = self.viewfiles['register_done_deferred_usercreated']
                viewargs['successmessage'] = successmessage
                # drop down to render
            else:
                # add errors to form
                form.merge_errordict(errordict)
                # re-force disabled field (email), since form may lose it if its disabled
                form.set_onevalue(verification.verification_varname, verification.verification_varval)
                # drop down and re-present form with errors
        else:
            # init form values from verification
            if (verification != None):
                # get any initial values for the form from the verification entry stored at the time they initially registered
                verification_userdict = verification.get_userdict()
                # add the verification code # so we can remember it and use it to look up when they submit this data
                verification_userdict['code'] = verification.verification_code
                # initialize form with these values
                form.set_values_from_dict(verification_userdict)

        # render form
        self.render_localview(viewfilename,viewargs)
        # success
        return None







































































    def create_newuser_deferred(self, userdict):
        """
        User has submitted a registration attempt with an accompanying validation code.
        There are a couple of things we need to do here:
        1. Re-check the verifcation code make sure it is good
        2. Start with pre-specified values in verification, overide using user-specified values that are allowed, IGNORE any changes to a field we used to validate (email)
        Return tuple (user, errordict, successmessage)
        """

        # first get verification and re-check that it's still valid
        verification_code = userdict['code']
        verification, failure = self.verify_registration_validatecode(verification_code)
        if (failure != None):
            # error with validation code -- set the message as generic error in errordict and return
            errordict = { '':failure.msg() }
            return None, errordict, ''
        
        # verified fields
        verifiedfields = [verification.verification_varname]

        # merge in verification values as defaults; this is useful if user pre-specified values at time of initial registration tht we aren't asking them about on this form
        # and FORCE in any verified value, even if we had it in form as if they could change it (e.g. email); this prevents a case where user verifies by email and then hacks a form to specify a different one when completeing their registration
        userdict = verification.update_dict_defaults_with_userdict(userdict, forcelist = verifiedfields)
        
        # ATTN: TODO it would be nice to explicitly check for email in use here, because if it is, there is no sense re-presenting the form since they can't change email
        # rather than simply trying to create user and re-presenting form if its in use, which will be confusing since we aren't letting them change their email
        # however, note that we DO check for this when they actually visit the link to verify -- so the only way this happens is if they visit the link to verify and while the form is onscreen waiting to be submitted, someone else completes verification with this email.

        # create user -- this will make sure email and username is available
        (user, errordict, successmessage) = self.create_newuser(userdict, verifiedfields=verifiedfields)
        if (errordict):
            # error
            return user, errordict, successmessage

        # success, so consume verification
        verification.consume(self.request)
        
        # let's log them in
        if (user != None):
            # tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
            self.request.set_user(user)
        
        # and return
        return user, errordict, successmessage        


