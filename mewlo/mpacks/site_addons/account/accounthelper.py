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
from forms.form_login_bycode import MewloForm_Login_ByCode
from forms.form_resend_register_verification import MewloForm_Resend_Register_Verification_Known, MewloForm_Resend_Register_Verification_Unknown




class AccountHelper(MewloRequestHandlerHelper):
    """This class is used to help processing requests.
    IMPORTANT NOTE: This class is instantiated on each request.  Thats important because we set request+response at init and then use it in calls.
    ATTN:TODO Change this to be like a manager and have a single instance shared.
    """

    # class constants (see also musermanager for duplication -- we need to centralize)
    DEF_VFTYPE_pre_user_verification = 'VFTYPE_pre_user_verification'
    DEF_VFTYPE_userfield_verification = 'VFTYPE_userfield_verification'


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

        # create the user immediate or defer via verification
        if (flag_immediate):
            # create user immediate
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
        (user, errordict, successmessage) = self.sitecomp_usermanager().create_user(self.request, userdict, verifiedfields=verifiedfields)
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

        # if there is a plaintext password specified we won't cache that in the verification, but instead cache the hashed version
        if ('password' in userdict):
            password_plain = userdict['password']
            del userdict['password']
            userdict['password_hashed'] = self.sitecomp_usermanager().hash_and_salt_password(password_plain)

        # the verification fields will contain the userdict so we can reinstate any values they provided at sign up time, when they confirm
        extradict = {'userdict':userdict}

        # before we create a new verification entry, we *may* sometimes want to delete/invalidate previous verification requests of same type from same user/session
        # note that we do NOT want to delete previous verifications just because they were sent to this same email address if the sessions were different
        verificationmanager.invalidate_previousverifications(verification_type, request, None)
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
        verification_varname = None
        failure = verificationmanager.basic_validation(verification, verification_code, self.request, verification_type_expected, is_shortcode_expected, verification_varname)
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
























    def handlepage_profile(self):
        """View user profile."""
        self.set_renderpageid('profile')
        # then page contents
        self.render_localview(self.viewfiles['profile'])
        # success
        return None









    def handlepage_verify_userfield(self):
        """handle user field verification."""
        self.set_renderpageid('userfield_verify')
        # get code from args
        args = self.request.get_route_parsedargs()
        verification_code = args['code']
        fieldname = args['field']

        # first get verification and re-check that it's still valid
        verification, failure = self.verify_userfield_validatecode(verification_code, fieldname)

        if (failure == None):
            # code matches, set the field and mark it verified
            failure = self.sitecomp_usermanager().set_userfield_from_verification(verification)
            if (failure == None):
                # success, so consume verification
                verification.consume(self.request)

        # render a page now
        if (failure == None):
            self.render_localview(self.viewfiles['userfield_verify_success'], {'fieldname': fieldname} )
        else:
            self.render_localview(self.viewfiles['userfield_verify_failure'], {'fieldname': fieldname, 'failure': failure.msg()})
        # success
        return None




    def verify_userfield_validatecode(self, verification_code, verification_varname):
        """Locate verification, check it for different kinds of errors.
        return tuple (verification, failure).
        """
        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()

        # find verification entry
        verification = verificationmanager.find_bylongcode(verification_code)

        # then check it
        verification_type_expected = self.DEF_VFTYPE_userfield_verification
        is_shortcode_expected = False
        failure = verificationmanager.basic_validation(verification, verification_code, self.request, verification_type_expected, is_shortcode_expected, verification_varname)
        # return success or failure
        return verification, failure





















































    def handlepage_resend_register_verification(self):
        """
        User has asked to be resent their initial registration verification email (for immediate registration method).
        If we can recognize their session and tie it to a new user verification, we will also offer to let them change their signup email at this point.
        If we can't recognize their session, and we still want to let them change their email, we can ask them for their username and password at this point (assuming we gathered it at time of registration).
        """
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('resend_register_verification')

        # what field are we re-verifying
        fieldname = 'email'

        # can we identify this client session with a pending reservation? (ie can we identify the user and the pending verification?)
        (user, verification) = self.try_find_pending_fieldverification_from_current_session(fieldname)

        if (user != None):
            # yes, we have identified the pending resgitration
            # init form+formdata
            formdata = self.request.get_postdata()
            # form to be used
            form = MewloForm_Resend_Register_Verification_Known(formdata)
            # default viewfilename
            viewfilename = form.get_viewfilename()
            viewargs = {'form':form}
            if (formdata != None and form.validate()):
                # they are submitting form -- so we want to resend the verification now (and possibly change the email on it)
                fieldval = form.get_val_nonblank(fieldname, user.getfield_byname(fieldname))
                failure = self.resend_field_verification(user, verification, fieldname, fieldval)
                if (not failure):
                    # success
                    viewfilename = self.viewfiles['verify_resent']
                    self.render_localview(viewfilename, viewargs)
                    return None
                # there was an error resending the verification, so add error and drop down
                form.add_genericerror(failure.msg())
            else:
                # initialize email field on blank form since we know who they are
                # should we use verification email or user email (they will be the same unless user requests new verifications and we always use user one)
                #form.setfield_ifblank(fieldname, user.getfield_byname(fieldname))
                form.setfield_ifblank(fieldname, verification.verification_varval)
                # then drop down to present form
        else:
            # we could not identify the prior unverified new registration, so we must be present them with form and ask them to tell us which account, etc.
            # init form+formdata
            formdata = self.request.get_postdata()
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
                    # BUT if they are trying to change the email address, they need to have provided their password -- that's the only way we can know it was them requesting it)
                    # ATTN: Though note, its possible they could have forgotten it, and if they havent confirmed registration yet, perhaps we shouldnt worry about them "PROVING" their identity, and we should treat it like anyone registering the username
                    failure = None
                    if (fieldval != user.getfield_byname(fieldname)):
                        password_plaintext = form.get_val('password')
                        does_passwordmatch = user.does_plaintextpasswordmatch(password_plaintext)
                        if (not does_passwordmatch):
                            failure = EFailure("You have specified a new email address, but your password did not match; your must provide the valid username and password in order to change your registration email address.")
                    if (not failure):
                        failure = self.resend_field_verification(user, verification, fieldname, fieldval)
                    if (not failure):
                        # success
                        viewfilename = self.viewfiles['verify_resent']
                        self.render_localview(viewfilename, viewargs)
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
        self.render_localview(viewfilename, viewargs)
        # success
        return None






    def try_find_pending_fieldverification_from_current_session(self, fieldname):
        """Try to find a pending new registration.
        Return tupe (User, Verification)."""

        # find pending registration verification based on request session
        verificationmanager = self.sitecomp_verificationmanager()
        verification_type = self.DEF_VFTYPE_userfield_verification
        verification = verificationmanager.find_valid_by_type_and_request(verification_type, self.request, fieldname)
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
            verification_type = self.DEF_VFTYPE_userfield_verification
            verification = verificationmanager.find_valid_by_type_and_userid(verification_type, user.id, fieldname)
            if (verification != None):
                return (user, verification)

        # failed
        return None, None




    def resend_field_verification(self, user, verification, fieldname, fieldval):
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
            verification.ip_created = self.request.get_remote_addr()
            isdirty = True

        # note that we do not change the code.. no point in doing so, right?

        # do we need to save verification?
        if (isdirty):
            verification.save()

        # ok now we need to send it
        email = verification.verification_varval
        failure = self.sitecomp_usermanager().send_field_verification_email_given_verification(verification, fieldname, email)
        return failure



































    def handlepage_reset_password(self):
        """
        User needs to reset their password because they can't remember it (this is different from a password-change once logged in.
        We just need to ask them for their username and/or email (both if we want to be more secure), and then we can send them a long verification code to reset (change) their password.
        They will return to this function with a code emailed to them to prove they are the owner of the account, at which point we can accept a new password from them.
        """
        # get args
        code = self.request.get_route_parsedarg('code','')














































    def handlepage_modify_field(self):
        """
        User wants to change a field (email, password, etc.).
        For some of these we may need to send them a verification before we can actually change it.
        NOTE: Eventually we will have nicer profile pages where they can change fields, this is more of an example to show the process involved when changing a field that needs a verification code sent.
        """
        # get code from args
        fieldname = self.request.get_route_parsedarg('field')





    def handlepage_modify_field_confirmation(self):
        """
        User is verifying a field modification by providing a code
        """
        # get code from args
        fieldname = self.request.get_route_parsedarg('code')

































    def handlepage_login_bycode(self):
        """
        This function lets a user login by verifying a code sent to them (via email).
        """
        # get code from args
        code = self.request.get_route_parsedarg('code','')

        # set page info first (as it may be used in page contents)
        self.set_renderpageid('login_bycode')
        # init form+formdata
        formdata = self.request.get_postdata()
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
            failure = self.try_loginbycode(code)
            if (not failure):
                # success, so we are done, called would have
                return None
            # error with code (set failure and drop down)
            form.add_fielderror('code',failure.msg())

        # show form
        self.render_localview(self.viewfiles['login_bycode'], {'form':form, 'failure': failuremsg} )





    def try_loginbycode(self, code):
        print "ATTN: TO DO CHECK CODE."
        failure = EFailure("Not implemented yet.")
        return failure