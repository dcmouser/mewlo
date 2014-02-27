"""
maccountmanager.py
This file contains helper code for account login and registration tyoe stuff
"""


# mewlo imports
from mewlo.mpacks.core.manager import manager
from mewlo.mpacks.core.form.mform import MewloForm
from mewlo.mpacks.core.user import muser, musermanager
from mewlo.mpacks.core.eventlog.mevent import EFailure, EException
from mewlo.mpacks.core.constants.mconstants import MewloConstants as mconst

# python imports

# addon imports
from forms.form_login import MewloForm_Login
from forms.form_register_immediate import MewloForm_Register_Immediate
from forms.form_register_deferred import MewloForm_Register_Deferred
from forms.form_register_deferred_finalize import MewloForm_Register_Deferred_Finalize
from forms.form_login_bycode import MewloForm_Login_ByCode
from forms.form_resend_register_verification import MewloForm_Resend_Register_Verification_Known, MewloForm_Resend_Register_Verification_Unknown
from forms.form_reset_password import MewloForm_Send_Reset_Password, MewloForm_Submit_Reset_Password
from forms.form_modifyfield_email import MewloForm_ModifyField_Email
from forms.form_generic_confirm import MewloForm_Generic_Confirm




class AccountManager(manager.MewloManager):
    """This class is used to help processing requests.
    """

    # class constants
    description = "Account management addon provides user login/registration functions"
    typestr = "siteaddon"



    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(AccountManager,self).__init__(mewlosite, debugmode)
        #
        self.viewbasepath = '${addon_account_path}/views/'
        #
        # we all of our non-form view files here, so that they are in one place (the forms themselves can specify their own default view files -- see form.get_viewfilename())
        self.viewfiles = {
            'logout_complete': 'logout_complete.jn2',
            #
            'register_done_immediate': 'register_done_immediate.jn2',
            'register_done_deferred_verification': 'register_done_deferred_verification.jn2',
            'register_done_deferred_usercreated': 'register_done_deferred_usercreated.jn2',
            'verify_registration_deferred_error_codenotfound': 'verify_registration_deferred_error_codenotfound.jn2',
            'verify_registration_deferred_error_emailinuse': 'verify_registration_deferred_error_emailinuse.jn2',
            'register_deferred_email_verificationsent': 'register_deferred_email_verificationsent.jn2',
            #
            'profile': 'profile.jn2',
            #
            'userfield_verify_success' : 'userfield_verify_success.jn2',
            'userfield_verify_failure' : 'userfield_verify_failure.jn2',
            #
            'login_bycode': 'login_bycode.jn2',
            #
            'verify_resent': 'verify_resent.jn2',
            #
            'reset_password_sent': 'reset_password_sent.jn2',
            'reset_password_verify_email': 'reset_password_verify_email.jn2',
            #
            'generic_verification_code_error' : 'generic_verification_code_error.jn2',
            'generic_success' : 'generic_success.jn2',
            'generic_error' : 'generic_error.jn2',
            'error_requires_login': 'error_requires_login.jn2',
            }


    def startup(self, eventlist):
        super(AccountManager,self).startup(eventlist)

    def shutdown(self):
        super(AccountManager,self).shutdown()












































































    def request_login(self, request):
        """Present and consume the login form.
        Return failure"""
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'login')
        # init form+formdata
        formdata = request.get_postdata()
        # the form we will use
        form = MewloForm_Login(formdata)

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            # build dictionary of parameters of registration
            userdict = form.data
            # now try logging in
            errordict = self.try_login(request, userdict)
            if (not errordict):
                # all good -- send them to profile view
                return self.request_profile(request)
                # success
                return None
            # drop down and re-present form with errors
            form.merge_errordict(errordict)

        # render form (use forms default view)
        self.render_localview(request, form.get_viewfilename(), {'form':form})
        # success
        return None



    def try_login(self, request, userdict):
        """Try logging in, return a dictionary of errors or REDIRECT if no error.
        Return error dictionary."""

        # try to log in the user
        user, errordict = self.sitecomp_usermanager().login_user(userdict)
        if (user != None):
            # ok it's a success, user was found and loaded.
            # tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
            request.set_user(user)
            # and now a message to show the user on the next page they load
            request.add_session_message('success',"You have successfully logged in.")
        # return success or error
        return errordict






















    def request_logout(self, request):
        """Present and consume the logour form.
        Return failure."""
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'logout')
        # logout
        self.try_logout(request, flag_clearsession=True)
        # then page contents
        self.render_localview(request, self.viewfiles['logout_complete'])
        # success
        return None



    def try_logout(self, request, flag_clearsession):
        """Just log the user out, and redirect them somewhere.
        Return failure"""
        # set session user to None (note they still keep their session, but it no longer has a user associated with it)
        request.clearloggedinuser()
        # should we also clear their session variable, which is good for testing?
        if (flag_clearsession):
            request.clearusersession()
        # and now a message to show the user on the next page they load
        # ATTN: This actually will actually cause a new session object to be created at this time if we just cleared the user session with flag_clearusersession -- which is a bit silly to combine them; but it does help test
        request.add_session_message('success',"You are now logged out.")
        # success
        return None























































    def request_register(self, request):
        """Controller function."""
#        return self.request_register_immediate(request)
        return self.request_register_deferred(request)


    def request_register_immediate(self, request):
        """Handle immediate registration case."""
        formclass = MewloForm_Register_Immediate
        return self.do_handlepage_register(request, formclass, flag_immediate = True)


    def request_register_deferred(self, request):
        """Handle deferred registration case."""
        formclass = MewloForm_Register_Deferred
        return self.do_handlepage_register(request, formclass, flag_immediate = False)







    def do_handlepage_register(self, request, formclass, flag_immediate):
        """Handle registration based on the formclass and type of registration."""
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'register')
        # init form+formdata
        formdata = request.get_postdata()
        # the form to be used
        form = formclass(formdata)

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            userdict = form.data
            # now try to register them
            (errordict, successmessage) = self.try_register(request, userdict, flag_immediate)
            if (not errordict):
                # success; called function will have handled rendering view, so we are now done and do not want to drop down
                return None
            else:
                # add errors to form
                form.merge_errordict(errordict)
                # drop down and re-present form with errors

        # render form
        self.render_localview(request, form.get_viewfilename(), {'form':form})
        # success
        return None















    def try_register(self, request, userdict, flag_immediate):
        """Try registering user.  On success, *WE* display success page.
        Return tupe (errordict, successmessage)."""

        # first let's see if we can find an existing user with this unique info -- if so, it's an error
        errordict = self.sitecomp_usermanager().error_if_user_exists(userdict)
        if (errordict):
            return errordict, ''

        # create the user immediate or defer via verification
        if (flag_immediate):
            # create user immediate
            (user, errordict, successmessage) = self.create_newuser(request, userdict)
            if (user != None):
                # a user was created; tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
                request.set_user(user)
            success_viewfile = self.viewfiles['register_done_immediate']
        else:
            # deferrred user creation, we create a verification instead
            (verification, errordict, successmessage) = self.precreate_newuser_deferred_justverification(request, userdict)
            success_viewfile = self.viewfiles['register_done_deferred_verification']

        if (not errordict):
            # success, we handle rendering page
            self.render_localview(request, success_viewfile, {'successmessage': successmessage})

        # return
        return (errordict, successmessage)
















    def create_newuser(self, request, userdict, verifiedfields=[]):
        """Create a new user right away.  Send them an email verification link after."""
        (user, errordict, successmessage) = self.sitecomp_usermanager().create_user(request, userdict, verifiedfields=verifiedfields)
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
        verification_type = mconst.DEF_VFTYPE_pre_user_verification
        # set verification_varname for quick lookup
        verification_varname = 'email'
        verification_varval = userdict['email']
        # other values
        is_shortcode = False
        expiration_days = 14

        # if there is a plaintext password specified we won't cache that in the verification, but instead cache the hashed version
        if ('password' in userdict):
            password_plain = userdict['password']
            del userdict['password']
            userdict['password_hashed'] = self.sitecomp_usermanager().hash_and_salt_password(password_plain)

        # the verification fields will contain the userdict so we can reinstate any values they provided at sign up time, when they confirm
        extradict = {'userdict':userdict}

        # before we create a new verification entry, we *may* sometimes want to delete/invalidate previous verification requests of same type from same user/session
        # note that we do NOT want to delete previous verifications just because they were sent to this same email address if the sessions were different
        verificationmanager.invalidate_previousverifications(verification_type, request, None, "It was canceled due to a more recent request.")
        # create it via verificationmanager
        verification = verificationmanager.create_verification(verification_type)
        # set it's properties
        verification.init_values(request, expiration_days, verification_varname, verification_varval, extradict, is_shortcode, None)
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
            errordict[mconst.DEF_FORM_GenericErrorKey] = failure.msg()

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

















































































    def request_register_deferred_verify(self, request):
        """Client visits deferred registration verification page."""
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'register_deferred_verify')
        # get code from args
        args = request.get_route_parsedargs()
        verification_code = args['code']
        # try to register -- caller will handle rendering the result
        return self.try_verify_registration_deferred_withcode(request, verification_code)






    def try_verify_registration_deferred_withcode(self, request, verification_code):
        """Try to complete their deferred verification given a code."""

        # look up the code
        verification, failure = self.verify_registration_validatecode(request, verification_code)
        if (failure != None):
            # ATTN: TODO - make this a form where they can provide the verification code manually
            self.render_localview(request, self.viewfiles['verify_registration_deferred_error_codenotfound'], {'failure':failure})
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
            self.render_localview(request, self.viewfiles['verify_registration_deferred_error_emailinuse'], {'failure':failure})
            return

        # ok email is still available, now we'd like to present them with a form that contains:
        # 1. the verification code as hidden var
        # 2. any pre-specified user profile values that they filled in during initial registration that we want to let them modify at this point
        # 3. their pre-specified email, fixed+disabled
        # 4. any additional other profile fields we want from them at this stage
        # only when they submit this successfully do we actually consume the verification entry and create their account

        # caller will handle rendering any page results
        return self.try_finalize_registration_deferred_withverification(request, verification)









    def verify_registration_validatecode(self, request, verification_code):
        """Locate verification, check it for different kinds of errors.
        return tuple (verification, failure).
        """
        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()

        # find verification entry
        verification = verificationmanager.find_bylongcode(verification_code)

        # then check it
        verification_type_expected = mconst.DEF_VFTYPE_pre_user_verification
        is_shortcode_expected = False
        verification_varname = None
        failure = verificationmanager.basic_validation(verification, verification_code, request, verification_type_expected, is_shortcode_expected, verification_varname)
        # return success or failure
        return verification, failure








    def try_finalize_registration_deferred_withverification(self, request, verification):
        """
        They have provided a valid registration code which we matched to a verification entry; now we will let them fill in the final form to create their account.
        See try_verify_registration_deferred_withcode for more info.
        """

        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'register_deferred_verify')
        # init form+formdata
        formdata = request.get_postdata()
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
            user, errordict, successmessage = self.create_newuser_deferred(request, userdict)
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
        self.render_localview(request, viewfilename,viewargs)
        # success
        return None







































































    def create_newuser_deferred(self, request, userdict):
        """
        User has submitted a registration attempt with an accompanying validation code.
        There are a couple of things we need to do here:
        1. Re-check the verifcation code make sure it is good
        2. Start with pre-specified values in verification, overide using user-specified values that are allowed, IGNORE any changes to a field we used to validate (email)
        Return tuple (user, errordict, successmessage)
        """

        # first get verification and re-check that it's still valid
        verification_code = userdict['code']
        verification, failure = self.verify_registration_validatecode(request, verification_code)
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
        (user, errordict, successmessage) = self.create_newuser(request, userdict, verifiedfields=verifiedfields)
        if (errordict):
            # error
            return user, errordict, successmessage

        # success, so consume verification
        verification.consume(request)

        # let's log them in
        if (user != None):
            # tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
            request.set_user(user)

        # and return
        return user, errordict, successmessage
























    def request_profile(self, request):
        """View user profile."""
        self.set_renderpageid(request, 'profile')

        user = request.get_user()
        if (user == None):
            self.render_localview( request, self.viewfiles['generic_error'], {'failuremessage': "No user information to display."})
            return None

        # then page contents
        self.render_localview( request, self.viewfiles['profile'], {'viewuser':user} )
        # success
        return None









    def request_userfield_verify(self, request):
        """handle user field verification."""
        self.set_renderpageid(request, 'userfield_verify')
        # get code from args
        args = request.get_route_parsedargs()
        verification_code = args['code']
        fieldname = args['field']

        # first get verification and re-check that it's still valid
        verification, failure = self.verify_userfield_validatecode(request, verification_code, fieldname)

        if (failure == None):
            # code matches, set the field and mark it verified
            failure = self.sitecomp_usermanager().set_userfield_from_verification(verification)
            if (failure == None):
                # success, so consume verification
                verification.consume(request)

        # render a page now
        if (failure == None):
            self.render_localview(request, self.viewfiles['userfield_verify_success'], {'fieldname': fieldname} )
        else:
            self.render_localview(request, self.viewfiles['userfield_verify_failure'], {'fieldname': fieldname, 'failure': failure.msg()})
        # success
        return None




    def verify_userfield_validatecode(self, request, verification_code, verification_varname):
        """Locate verification, check it for different kinds of errors.
        return tuple (verification, failure).
        """
        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()

        # find verification entry
        verification = verificationmanager.find_bylongcode(verification_code)

        # then check it
        verification_type_expected = mconst.DEF_VFTYPE_userfield_verification
        is_shortcode_expected = False
        failure = verificationmanager.basic_validation(verification, verification_code, request, verification_type_expected, is_shortcode_expected, verification_varname)
        # return success or failure
        return verification, failure





















































    def request_resend_register_verification(self, request):
        """
        User has asked to be resent their initial registration verification email (for immediate registration method).
        If we can recognize their session and tie it to a new user verification, we will also offer to let them change their signup email at this point.
        If we can't recognize their session, and we still want to let them change their email, we can ask them for their username and password at this point (assuming we gathered it at time of registration).
        """
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'resend_register_verification')

        # what field are we re-verifying
        fieldname = 'email'

        # can we identify this client session with a pending reservation? (ie can we identify the user and the pending verification?)
        (user, verification) = self.try_find_pending_fieldverification_from_current_session(fieldname)

        if (user != None):
            # yes, we have identified the pending resgitration
            # init form+formdata
            formdata = request.get_postdata()
            # form to be used
            form = MewloForm_Resend_Register_Verification_Known(formdata)
            # default viewfilename
            viewfilename = form.get_viewfilename()
            viewargs = {'form':form, 'verifyuser': user}
            if (formdata != None and form.validate()):
                # they are submitting form -- so we want to resend the verification now (and possibly change the email on it)
                fieldval = form.get_val_nonblank(fieldname, user.getfield_byname(fieldname))
                failure = self.resend_field_verification(user, verification, fieldname, fieldval)
                if (not failure):
                    # success
                    viewfilename = self.viewfiles['verify_resent']
                    self.render_localview(request, viewfilename, viewargs)
                    return None
                # there was an error resending the verification, so add error and drop down
                form.add_genericerror(failure.msg())
            else:
                # initialize email form field on blank form since we know who they are
                # should we use verification email or user email (they will be the same unless user requests new verifications and we always use user one)
                #form.setfield_ifblank(fieldname, user.getfield_byname(fieldname))
                form.setfield_ifblank(fieldname, verification.verification_varval)
                # then drop down to present form
        else:
            # we could not identify the prior unverified new registration by the client session, so we must be present them with form and ask them to tell us which account, etc.
            # init form+formdata
            formdata = request.get_postdata()
            # form to be used
            form = MewloForm_Resend_Register_Verification_Unknown(formdata)
            # default viewfilename
            viewfilename = form.get_viewfilename()
            viewargs = {'form':form}
            if (formdata != None and form.validate()):
                # they are submitting form -- so we want to try to find the verification now
                userdict = form.data
                # find user and verification
                (user, verification) = self.try_find_pending_fieldverification_from_userdict(userdict, fieldname)
                if (user != None):
                    # we found them and they are indeed waiting for verification, so resend it
                    fieldval = form.get_val_nonblank(fieldname, user.getfield_byname(fieldname))
                    # BUT if they are trying to change the email address, should we require them to provide their password? that's the only way we can know it was really the same person who signed up who is changing the email)
                    # ATTN: Though note, its possible they could have forgotten it, and if they havent confirmed registration yet, perhaps we shouldnt worry about them "PROVING" their identity, and we should treat it like anyone registering the username
                    # we will see if their is a password value on form, if not, then we wont care about it; so it's up to us at time of form creation
                    failure = None
                    if (fieldval != user.getfield_byname(fieldname)):
                        if (form.hasfield('password')):
                            password_plaintext = form.get_val('password')
                            does_passwordmatch = user.does_plaintextpasswordmatch(password_plaintext)
                            if (not does_passwordmatch):
                                failure = EFailure("You have specified a new email address, but your password did not match; your must provide the valid username and password in order to change your registration email address.")
                        else:
                            # no password to check -- before we let them change this without a password, we make damn sure this is a NEW user account
                            if (not user.is_safe_stranger_claim_thisaccount()):
                                failure = EFailure("Email cannot be changed from this form on an existing active user account; login first to change email address.")
                    if (not failure):
                        failure = self.resend_field_verification(user, verification, fieldname, fieldval)
                    if (not failure):
                        # success
                        viewfilename = self.viewfiles['verify_resent']
                        self.render_localview(request, viewfilename, viewargs)
                        return None
                else:
                    # couldn't find them, that's an error
                    failure = EFailure("Could not find any pending new user registration using the info you have provided.")
                # there was an error resending the verification, so add error and drop down
                form.add_genericerror(failure.msg())
                # drop down to present form
            else:
                # initialization of form or error on form, drop down
                pass

        # render form
        self.render_localview(request, viewfilename, viewargs)
        # success
        return None





    def try_find_pending_fieldverification_from_current_session(self, request, fieldname):
        """Try to find a pending new registration.
        Return tupe (User, Verification)."""

        # find pending registration verification based on request session
        verificationmanager = self.sitecomp_verificationmanager()
        verification_type = mconst.DEF_VFTYPE_userfield_verification
        verification = verificationmanager.find_valid_by_type_and_request(verification_type, request, fieldname)
        if (verification != None):
            # ok we got the verification, now get the user it corresponds to
            user = self.sitecomp_usermanager().finduser_byid(verification.user_id)
            if (user != None):
                # ATTN: we found user -- at some point we might want to check to make sure it hasn't become deleted, etc; though there is no harm if we send them a new verification, just means they will get an error later when they try to use it.
                return (user, verification)

        # failed
        return None, None



    def try_find_pending_fieldverification_from_userdict(self, userdict, fieldname):
        """Try to find a pending new registration.
        Return tupe (User, Verification)."""

        # first we need to find the user
        user = self.sitecomp_usermanager().find_user_by_dict(userdict)
        if (user != None):
            # now find pending registration verification based on request session
            verificationmanager = self.sitecomp_verificationmanager()
            verification_type = mconst.DEF_VFTYPE_userfield_verification
            verification = verificationmanager.find_valid_by_type_and_userid(verification_type, user.id, fieldname)
            if (verification != None):
                return (user, verification)

        # failed
        return None, None




    def resend_field_verification(self, request, user, verification, fieldname, fieldval):
        """Resend a new user their pending registration verification email.
        If a different email address is specified, CHANGE AND SAVE the verification (and user?) email field first.
        Return None on success, otherwise failure."""

        # init
        isdirty = True

        # modify field value (email) if appropriate
        if ((fieldval != None) and (fieldval != '') and (verification.verification_varval != fieldval)):
            verification.verification_varval = fieldval
            isdirty = True

        # ATTN:TODO - should we update expiration date? what about ip and sesssion? does it matter?
        if (False):
            expiration_dist = verification.date_expires - verification.date_created
            verification.date_expires = self.get_nowtime() + expiration_dist
            verification.ip_created = request.get_remote_addr()
            isdirty = True

        # note that we do not change the code.. no point in doing so, right?

        # do we need to save verification?
        if (isdirty):
            verification.save()

        # ok now we need to send it
        email = verification.verification_varval
        failure = self.sitecomp_usermanager().send_field_verification_email_given_verification(verification, fieldname, email)
        return failure



































    def request_send_reset_password(self, request):
        """
        User needs to reset their password because they can't remember it (this is different from a password-change once logged in.
        We just need to ask them for their username and/or email (both if we want to be prevent nuisance filings), and then we can send them a long verification code to reset (change) their password.
        They will return to this function with a code emailed to them to prove they are the owner of the account, at which point we can accept a new password from them.
        If we are nice we might recognize them if they are logged in via session, and pre-fill their username+email address.
        """
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'send_reset_password')

        # form
        formdata = request.get_postdata()
        form = MewloForm_Send_Reset_Password(formdata)
        viewfilename = form.get_viewfilename()
        viewargs = {'form':form }
        if (formdata == None):
            # initialize form; can we get user from session?
            user = request.get_user()
            if (user != None):
                # let's be nice and pre-fill in the form for them
                form.set_values_from_dict( {'username':user.username, 'email':user.email} )
        elif (form.validate()):
            # they are submitting (valid) form
            # locate user using the info they've given us
            userdict = form.data
            user = self.sitecomp_usermanager().find_user_by_dict(userdict)

            if (user != None):
                # found user, send them a password reset
                failure = self.try_send_passwordreset(user)
            else:
                failure = EFailure("Could not locate a user account using the information you've provided.")

            if (not failure):
                # success
                viewfilename = self.viewfiles['reset_password_sent']
                self.render_localview(request, viewfilename, viewargs)
                return None

            # there was an error resending the verification, so add error and drop down
            form.add_genericerror(failure.msg())

        # render form
        self.render_localview(request, viewfilename, viewargs)
        return None




    def try_send_passwordreset(self, request, user):
        """Send the user a password reset verification code."""

        # create the verification
        verification_type = mconst.DEF_VFTYPE_user_passwordreset
        fieldname = 'password'
        fieldval = ''
        extradict = {}
        is_shortcode = False
        flag_invalidateprevious = True
        #
        (verification, failure) = self.sitecomp_usermanager().build_generic_user_verification(verification_type, user, request, fieldname, fieldval, extradict, is_shortcode, flag_invalidateprevious)
        if (failure):
            return failure
        # email it to the user
        emailaddress = user.email
        emailtemplatefile = self.calc_localtemplatepath(self.viewfiles['reset_password_verify_email'])
        verificationurl = self.calc_verificationurl_passwordreset(verification)
        maildict = {
            'to': [ emailaddress ],
            'subject': "Password reset verification",
            'body': self.get_mewlosite().renderstr_from_template_file(emailtemplatefile, {'verificationurl':verificationurl})
        }
        # now send it
        failure = self.sitecomp_mailmanager().send_email(maildict)

        # success
        return failure



    def calc_verificationurl_passwordreset(self, verification):
        """Build url user should visit to verify."""
        url = self.get_mewlosite().build_routeurl_byid('reset_password', flag_relative=False, args={'code':verification.verification_code} )
        return url



















    def request_reset_password(self, request):
        """
        User is ready to provide their new (reset) password, and a verification code to prove they are the owner of the account.
        This is very much like deferred account finalization, where the verification code is put as a hidden field on a form that they will resubmit with their changes.
        """
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'reset_password')

        # get args
        verification_code = request.get_route_parsedarg('code','')
        # try to register -- caller will handle rendering the result
        return self.try_reset_password_withcode(request, verification_code)




    def try_reset_password_withcode(self, request, verification_code):
        """Try to complete password reset given a code."""

        # look up the code, make sure its valid, unused and unexpired, of the right type, etc.
        (verification, failure) = self.validatecode_passwordreset(request, verification_code)
        if (failure != None):
            # ATTN: TODO - make this a form where they can provide the verification code manually
            self.render_localview(request, self.viewfiles['generic_verification_code_error'], {'failure':failure})
            return

        # code is good
        return self.try_reset_password_withverification(verification)







    def validatecode_passwordreset(self, request, verification_code):
        """
        Locate verification, make sure it's good
        Return tuple (verification, failure).
        """
        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()

        # find verification entry
        verification = verificationmanager.find_bylongcode(verification_code)

        # then check it
        verification_type_expected = mconst.DEF_VFTYPE_user_passwordreset
        is_shortcode_expected = False
        verification_varname = 'password'
        failure = verificationmanager.basic_validation(verification, verification_code, request, verification_type_expected, is_shortcode_expected, verification_varname)
        # return success or failure
        return (verification, failure)





    def try_reset_password_withverification(self, request, verification):
        """Present them with a form to reset their password."""

        # get user from verification
        verificationmanager = self.sitecomp_verificationmanager()
        user = verificationmanager.get_user_from_verification(verification)

        # init form+formdata
        formdata = request.get_postdata()
        # form to be used
        form = MewloForm_Submit_Reset_Password(formdata)

        # default viewfilename
        viewfilename = form.get_viewfilename()
        viewargs = {'form':form, 'viewuser':user}

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            password_plaintext = form.get_val('password')
            # now try to set update user's password
            failure = self.do_reset_password(user, password_plaintext)
            if (not failure):
                # success; now we want to consume this verification
                verification.consume(request)
                # and drop down to view sucess
                viewfilename = self.viewfiles['generic_success']
                viewargs['successmessage'] = "Your password has been successfully changed."
            else:
                # add error to form
                form.add_genericerror(failure.msg())
                # drop down and re-present form with errors
        else:
            # init form values from verification
            if (verification != None):
                # get any initial values for the form from the verification entry stored at the time they initially registered
                # initialize form with these values
                form.set_values_from_dict( {'code':verification.verification_code} )

        # render form
        self.render_localview(request, viewfilename, viewargs)
        # success
        return None




    def do_reset_password(self, user, password_plaintext):
        """Change a user's password."""
        self.sitecomp_usermanager().set_userpassword_from_plaintext(user, password_plaintext)
        user.save()
        return None





























    def request_modify_field(self, request):
        """
        User wants to change a field (email, password, etc.).
        For some of these we may need to send them a verification before we can actually change it.
        NOTE: Eventually we will have nicer profile pages where they can change fields, this is more of an example to show the process involved when changing a field that needs a verification code sent.
        """
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'modify_field')

        # get logged in user from session (required)
        user = request.get_user()
        if (user == None):
            self.render_localview(request, self.viewfiles['error_requires_login'], {} )
            return None

        # get fieldname to be modified from args
        fieldname = request.get_route_parsedarg('field')

        # now try to modify it -- we only know how to handle certain fields
        if (fieldname == 'email'):
            self.try_modify_field_form(request, user, fieldname, MewloForm_ModifyField_Email)
        else:
            # unsupported field, error
            self.render_localview(request, self.viewfiles['generic_error'], {'failuremessage':'Error: Unsupported fieldname specified.'} )
            # success
            return None

        return



    def try_modify_field_form(self, request, user, fieldname, formclass):
        """Present form where user can modify field."""

        # init form+formdata
        formdata = request.get_postdata()
        # form to be used
        form = formclass(formdata)

        # default viewfilename
        viewfilename = form.get_viewfilename()
        viewargs = {'form':form, 'viewuser':user}

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            fieldval = form.get_val(fieldname)
            # now try to set update user's password
            (successmessage, failure) = self.try_modify_field_with_verification(request, user, fieldname, fieldval)
            if (not failure):
                # success, we've modified the field (or created a verification to do so); and drop down to view sucess
                viewfilename = self.viewfiles['generic_success']
                viewargs['successmessage'] = successmessage
            else:
                # add error to form
                form.add_genericerror(failure.msg())
                # drop down and re-present form with errors

        # render form
        self.render_localview(request, viewfilename, viewargs)
        # success
        return None



    def try_modify_field_with_verification(self, request, user, fieldname, fieldval):
        """Modify the field or create a deferred field modification if it needs verification.
        return tuple (successmessage,failure).
        """

        # if it's a unique field we need to make sure no one else has it -- though note that even if it sneaks through us here, it will be caught again at time of confirmation

        if (fieldname == 'email'):
            # modify email
            failure = self.sitecomp_usermanager().check_uniquefield_notinuse(user, fieldname, fieldval)
            if (failure != None):
                return ('', failure)
            failure = self.sitecomp_usermanager().send_onefield_verification(user, request, fieldname, fieldval)
            successmessage = "A verification email has been sent to the new address you have provided.  Your new e-mail address will go into effect when you verify the code in that email."
            return (successmessage, failure)

        # unsupported
        return EFailure('Unsupported fieldname in try_modify_field_with_verification().')








    def request_cancel_modify_field(self, request):
        """
        User wants to cancel a pending verification of a changed field request (email, password, etc.).
        NOTE: Eventually we will have nicer profile pages where they can change fields, this is more of an example to show the process involved when changing a field that needs a verification code sent.
        """
        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'modify_field')

        # get fieldname to be modified from args
        fieldname = request.get_route_parsedarg('field')

        # try it
        failure = self.try_cancel_modify_field_form(request, fieldname)
        return None



    def try_cancel_modify_field_form(self, request, fieldname):
        """Cancel a pending verification for field change request."""

        # get logged in user from session (required)
        user = request.get_user()
        if (user == None):
            self.render_localview(request, self.viewfiles['error_requires_login'], {} )
            return None

        # init form+formdata
        formdata = request.get_postdata()
        # form to be used
        form = MewloForm_Generic_Confirm()

        # default viewfilename
        viewfilename = form.get_viewfilename()
        viewargs = {'form':form, 'viewuser':user, 'message':"Are you sure you wish to cancel pending field change?"}

        # cancel/delete
        invalidreason = "Canceled by user request."

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            failure = self.try_cancel_modify_field(request, user, fieldname, invalidreason)
            if (failure):
                self.render_localview(request, self.viewfiles['generic_error'], {'failuremessage':"Failed to cancel pending field change: {1}.".format(fieldname,failure.msg())} )
            else:
                self.render_localview(request, self.viewfiles['generic_success'], {'successmessage':"Previous pending modification of field {0} has been canceled.".format(fieldname)} )
            return None

        # render form
        self.render_localview(request, viewfilename, viewargs)
        # success
        return None




    def try_cancel_modify_field(self, request, user, fieldname, invalidreason):
        """Cancel a pending verification for field change request."""
        # now try to modify it -- we only know how to handle certain fields
        if (fieldname == 'email'):
            failure = self.sitecomp_usermanager().cancel_userfield_verifications(user, request, fieldname, invalidreason)
        else:
            # unsupported field, error
            failure = EFailure("Error: Unsupported fieldname specified.")
        return failure












# THE BELOW CODE IS NOT USED YET




    def request_login_bycode(self, request):
        """
        This function lets a user login by verifying a code sent to them (via email).
        """
        # get code from args
        code = request.get_route_parsedarg('code','')

        # set page info first (as it may be used in page contents)
        self.set_renderpageid(request, 'login_bycode')
        # init form+formdata
        formdata = request.get_postdata()
        # form to be used
        form = MewloForm_Login_ByCode(formdata)

        # default viewfilename
        viewfilename = form.get_viewfilename()
        failuremsg = ''

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid, get the code specified and drop down
            code = form.get_val('code','')
        else:
            # initialize form
            form.set_values_from_dict( {'code':code} )

        # if code is specified, check it
        if (code != ''):
            failure = self.try_loginbycode(request, code)
            if (not failure):
                # success, so we are done, called would have
                return None
            # error with code (set failure and drop down)
            form.add_fielderror('code',failure.msg())

        # show form
        self.render_localview(request, self.viewfiles['login_bycode'], {'form':form, 'failure': failuremsg} )





    def try_loginbycode(self, request, code):
        print "ATTN: TO DO CHECK CODE."
        failure = EFailure("Not implemented yet.")
        return failure