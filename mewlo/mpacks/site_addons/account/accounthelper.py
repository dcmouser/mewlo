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
from forms.form_register_justemail import MewloForm_Register_JustEmail
from forms.form_register_usernamepassemail import MewloForm_Register_UsernamePasswordEmail
from forms.form_register_stage2 import MewloForm_Register_Stage2




class AccountHelper(MewloRequestHandlerHelper):
        
    # class constants
    DEF_VFTYPE_pre_user_verification = 'VFTYPE_pre_user_verification'



    def __init__(self, request, response):
        # call parent constructor
        super(AccountHelper, self).__init__(request, response)
        #
        self.viewbasepath = '${addon_account_path}/views/'
        #
        # we all of our non-form view files here, so that they are in one place (the forms specify their own default view files -- see form.get_viewfilename())
        self.viewfiles = {
            'register_complete': 'register_complete.jn2',
            'login_complete': 'login_complete.jn2',
            'logout_complete': 'logout_complete.jn2',
            'verify_registration_complete': 'verify_registration_complete.jn2',
            'verify_registration_codenotfound': 'verify_registration_codenotfound.jn2',
            'email_verificationsent': 'email_verificationsent.jn2',
            'verify_registration_postverify_emailinuse': 'verify_registration_postverify_emailinuse.jn2',
            'register2_complete': 'register2_complete.jn2',
            }






    
    

    def renderpage_login(self):
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('login')
        # init form+formdata
        formdata = self.request.get_postdata()
        form = MewloForm_Login(formdata)

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            # build dictionary of parameters of registration
            user_dict = form.data
            #user_dict = {'username': form.username.data, 'password': form.password.data}
            # now try logging in
            errordict = self.try_login(user_dict)
            if ((errordict == None) or (len(errordict)==0)):
                # all good
                self.render_localview(self.viewfiles['login_complete'])
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
        
        # default viewfilename
        viewfilename = form.get_viewfilename()
        viewargs = {'form':form}

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            # build dictionary of parameters of registration
            user_dict = form.data
            #user_dict = {'username': form.username.data, 'password': form.password.data, 'email': form.email.data}
            # now try to register them
            user, errordict, successmessage = self.try_register(user_dict)
            if ((errordict == None) or (len(errordict)==0)):
                # success
                viewfilename = self.viewfiles['register_complete']
                viewargs['successmessage'] = successmessage
                # drop down to render
            else:
                # add errors to form
                form.merge_errordict(errordict)
                # drop down and re-present form with errors

        # render form
        self.render_localview(viewfilename,viewargs)
        # success
        return None















    def renderpage_logout(self):
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('logout')

        # logout
        self.try_logout()

        # then page contents
        self.render_localview(self.viewfiles['logout_complete'])
        # success
        return None








    def renderpage_verify_registration(self):
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('verify_registration')
        # logout
        self.try_verify_registration()
        # success
        return None








































































    def try_logout(self):
        """Just log the user out, and redirect them somewhere."""
        # set session user to None (note they still keep their session, but it no longer has a user associated with it)
        self.request.clearloggedinuser()
        return None







    def try_login(self, user_dict):
        """Try logging in, return a dictionary of errors or REDIRECT if no error."""

        # try to log in the user
        user, errordict = self.sitecomp_usermanager().login_user(user_dict)
        if (user != None):
            # ok it's a success, user was found and loaded.
            # tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
            self.request.set_user(user)
            
        return errordict










    def try_register(self, user_dict):
        """Try registering user, return a dictionary of errors or REDIRECT if no error."""

        # first let's see if we can find the user
        errordict = self.sitecomp_usermanager().error_if_user_exists(user_dict)
        if (len(errordict)>0):
            return None, errordict, ''

        # create the user instantly or defer via verification
        if (False):
            # create user instantly
            (user, errordict, successmessage) = self.sitecomp_usermanager().create_user(user_dict)
        else:
            # verification step before creating user
            (verification, errordict, successmessage) = self.create_newuser_verification(self.request, user_dict)
            user = None
        
        if (user != None):
            # ok it's a success, user was created.
            # tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
            self.request.set_user(user)

        return (user, errordict, successmessage)










    def create_newuser_verification(self, request, userdict):
        """
        Create a verification entry for a new user registration.
        We take a userdict instead of explicit variables for username, email, password, so that we can eventually accomodate whatever initial user properties we have specified at time of registration.
        return tuple (userobject, errordict, successmessage); if there are errors return them and userobject as None
        """
        errordict = {}

        # first let's see if we can find the user
        errordict = self.sitecomp_usermanager().error_if_user_exists(userdict)
        if (len(errordict)>0):
            return None, errordict, ''

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

        # before we create a new verification entry, we *may* sometimes want to delete previous verification requests of same type from same user
        verificationmanager.invalidate_previousverifications(verification_type, request)
        # create it via verificationmanager
        verification = verificationmanager.create_verification(verification_type)
        # set it's properties
        verification.init_values(request, expiration_days, verification_varname, verification_varval, extradict, is_shortcode)
        # save it
        verification.save()
        
        # now send them an email telling them how to verify
        emailtemplatefile = self.calc_localtemplatepath(self.viewfiles['email_verificationsent'])
        verificationurl = self.calc_verificationurl(verification)
        maildict = {
            'to': [ userdict['email'] ],
            'subject': u'Signup verification email',
            'body': self.get_mewlosite().renderstr_from_template_file(emailtemplatefile, {'verificationurl':verificationurl})
        }
        failure = self.sitecomp_mailmanager().send_email(maildict)
        if (failure != None):
            errordict[''] = str(failure)
        
        # message to be displayed to user
        successmessage = 'Your account has been registered, but your email must be verified before you can login.  Check your email for your verification code.'
        
        # return it
        return None, errordict, successmessage





    
    def calc_verificationurl(self, verification):
        """Compute the verification url for a verification object.
        This will require asking the site what the base url should be.
        """
        url = self.get_mewlosite().build_routeurl_byid('verify_registration', flag_relative=False, args={'code':verification.verification_code} )
        return url













    def verify_registration_validatecode(self, verification_code):
        """Locate verification, check it for different kinds of errors.
        return tuple (failure, verification).
        """
        
        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()        
        
        # find verification entry
        verification = verificationmanager.find_bylongcode(verification_code)
        
        # check it - verification entry found
        verification_type_expected = self.DEF_VFTYPE_pre_user_verification
        is_shortcode_expected = False
        failure = verificationmanager.basic_validation(verification, verification_code, self.request, verification_type_expected, is_shortcode_expected)
        if (failure != None):
            return verification, failure

        # all good
        return verification, None












    def try_verify_registration(self):
        """Try to complete their verification."""

        # get code from args
        args = self.request.get_route_parsedargs()
        verification_code = args['code']
        return self.try_verify_registration_withcode(verification_code)

    
    def try_verify_registration_withcode(self, verification_code):
        """Try to complete their verification."""

        verification, failure = self.verify_registration_validatecode(verification_code)

        if (failure != None):
            # ATTN: TODO - make this a form where they can provide the verification code manually
            self.render_localview(self.viewfiles['verify_registration_codenotfound'], {'failure':failure})
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
        if (len(errordict) > 0):
            # another user has this email, sorry sucker
            self.render_localview(self.viewfiles['verify_registration_postverify_emailinuse'], {'failure':failure})
            return

        # ok email is still available, now we'd like to present them with a form that contains: 1. the verification code as hidden var, 2. any pre-specified user profile values, 3. their pre-specified email, fixed+disabled, 4. any other profile fields we want from them
        # only when they submit this do we actually consume the verification entry and create their account
        
        return self.stage2registration_with_verification(verification)
    
    

    
    
    def stage2registration_with_verification(self, verification):
        """
        They have provided a valid registration code, now we will let them provide the final form to create their account.
        See try_verify_registration_withcode for more info.
        """
        
        return self.renderpage_state2register(verification)





    def renderpage_state2register(self, verification=None):
        # set page info first (as it may be used in page contents)
        self.set_renderpageid('register')
        # init form+formdata
        formdata = self.request.get_postdata()
        form = MewloForm_Register_Stage2(formdata)

        # If we want we can remove form fields here like so:
        #delattr(form, 'accept_rules')
        

        # default viewfilename
        viewfilename = form.get_viewfilename()
        viewargs = {'form':form}

        # valid submission?
        if (formdata != None and form.validate()):
            # form data is valid
            # build dictionary of parameters of registration
            user_dict = form.data
            #user_dict = {'username': form.username.data, 'password': form.password.data, 'email': form.email.data}
            # now try to register them
            user, errordict, successmessage = self.try_register2(user_dict)
            if ((errordict == None) or (len(errordict)==0)):
                # success
                viewfilename = self.viewfiles['register2_complete']
                viewargs['successmessage'] = successmessage
                # drop down to render
            else:
                # add errors to form
                form.merge_errordict(errordict)
                # drop down and re-present form with errors
        else:
            # init form values from verification
            if (verification != None):
                verification_user_dict = verification.get_userdict()
                verification_user_dict['code'] = verification.verification_code
                form.set_values_from_dict(verification_user_dict)
                print "ATTN:DEBUG initial values = "+str(verification_user_dict)
            

        # render form
        self.render_localview(viewfilename,viewargs)
        # success
        return None



    def try_register2(self, user_dict):
        """
        User has submitted a registration attempt with an accompanying validation code.
        There are a couple of things we need to do here:
        1. Re-check the verifcation code make sure it is good
        2. Start with pre-specified values in verification, overide using user-specified values that are allowed, IGNORE any changes to a field we used to validate (email)
        Return tuple (user, errordict, successmessage)
        """

        print "ATTN: in try_register2 with user_dict = "+str(user_dict)

        # first get verification and check that it's still valid
        verification_code = user_dict['code']
        verification, failure = self.verify_registration_validatecode(verification_code)
        if (failure != None):
            # error with validation code
            errordict = {'':failure.msg()}
            return None, errordict, ''

        # merge in verification values over defaults; this is useful if user pre-specified values we aren't asking them about on this form
        verifcation_userdict = verification.get_userdict()
        for key,val in verifcation_userdict.iteritems():
            if (key not in user_dict):
                user_dict[key]=val
        # and now FORCE in any verified value, even if we had it in form as if they could change it (e.g. email)
        user_dict[verification.verification_varname] = verification.verification_varval
        
        print "ATTN: in try_register2 stage 2 with user_dict = "+str(user_dict)

        # ATTN: it would be nice to check for email in use here, because if it is, there is no sense re-presenting the form since they can't change email

        # create user -- this will make sure email and username is available
        (user, errordict, successmessage) = self.sitecomp_usermanager().create_user(user_dict)

        if ((errordict != None) and (len(errordict)>0)):
            # error
            return user, errordict, successmessage


        # success, so consume verification
        verification.consume(self.request)

        
        # let's log them in
        if (user != None):
            # tell the session about the user's identity (i.e. the client browser BECOMES this new user and is logged in immediately)
            self.request.set_user(user)
        
        return user, errordict, successmessage        


