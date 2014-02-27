"""
musermanager.py

The helper manager for user model.

"""



# mewlo imports
from ..manager import modelmanager
from ..helpers import misc
import muser
from ..eventlog.mevent import EFailure, EException
from ..constants.mconstants import MewloConstants as mconst

# python imports





class MewloUserManager(modelmanager.MewloModelManager):
    """User model manager."""




    def __init__(self, mewlosite, debugmode):
        # parent constructor -- pass in the main modelclass we manager
        super(MewloUserManager,self).__init__(mewlosite, debugmode, muser.MewloUser)
        # also keep track of temp user
        self.modelclass_tempuser = muser.MewloUserTemp
        #
        # we all of our non-form view files here, so that they are in one place (the forms themselves can specify their own default view files -- see form.get_viewfilename())
        self.viewfiles = {
            'user_verify_field_email': 'user_verify_field_email.jn2',
        }




    def startup(self, eventlist):
        super(MewloUserManager,self).startup(eventlist)

    def shutdown(self):
        super(MewloUserManager,self).shutdown()





    def getmake_guestuserobject(self):
        """
        Make a guest user object and return it.
        Ultimately I think that "making" a guest user object, should probably involve loading a specific guest user account from database.
        ATTN: unfinished.
        """
        # ATTN: test -- for now just return a new object
        user = self.modelclass_tempuser()
        return user



    def create_user(self, request, userdict, verifiedfields):
        """
        Make a new user account.
        We take a userdict instead of explicit variables for username, email, password, so that we can eventually accomodate whatever initial user properties we have specified at time of registration.
        return tuple (userobject, errordict); if there are errors return them and userobject as None
        """
        errordict = {}

        # make sure unique fields (username, email) are unique; error if not
        errordict = self.error_if_user_exists(userdict)
        if (errordict):
            # errors
            return None, errordict, ''

        # create user account.
        user = self.modelclass()
        user.username = userdict['username']
        user.email = userdict['email']

        # password -- hash it if its plaintext, or use pre-hashed version (if both provided we will ignored the pre-hashed one)
        if ('password' in userdict):
            self.set_userpassword_from_plaintext(user, userdict['password'])
        elif ('password_hashed' in userdict):
            user.password_hashed = userdict['password_hashed']

        # verified email is special
        if ('email' in verifiedfields):
            user.isverified_email = True
        else:
            user.isverified_email = False

        # ATTN:TODO handle other verifiedfields

        # no errors, save it
        # ATTN: to do check for save errors
        user.save()

        # any field verifications needed?
        self.send_field_verifications(user, request, verifiedfields)

        # success
        successmessage = 'User account has been successfully created.'

        # return success or error
        return user, errordict, successmessage


    def set_userpassword_from_plaintext(self, user, password_plaintext):
        """set hashed password."""
        user.password_hashed = self.hash_and_salt_password(password_plaintext)


















































    def send_field_verifications(self, user, request, verifiedfields):
        """This is generally called right after saving a new user who needs to be sent an email verification."""
        # what fields need verifications?
        required_verifiedfields = ['email']
        # now see which ones they need
        for fieldname in required_verifiedfields:
            if (fieldname in verifiedfields):
                # fieldname is explicitly marked as verified, so nothing to check
                continue
            else:
                # ok this is a field that needs verification
                # email is special; but we might add a check for property isverified_FIELDNAME to allow other hardcoded explicit verified columns
                (fieldval,isverified) = user.get_fieldvalue_and_verificationstatus(fieldname)
                if (isverified):
                    # it's already verified, so nothing to do
                    continue
                if (fieldval == None):
                    # it's blank, so nothing to do
                    continue
            # ok we have a non-blank field requiring verification
            failure = self.send_onefield_verification(user, request, fieldname, fieldval)







    def send_onefield_verification(self, user, request, fieldname, fieldval):
        """Send user a field verification message.
        Typically this is for email.
        Return failure."""
        if (fieldname == 'email'):
            # email verification
            return self.send_field_verification_email(user, request, fieldval)

        # ATTN: we don't know how to handle other types of fields yet
        return EFailure('Unsupported fieldname in send_onefield_verification.')



    def send_field_verification_email(self, user, request, emailaddress):
        """Send an email verification."""
        # generate the verification code they need
        fieldname = 'email'
        (verification, failure) = self.build_userfield_verification(user, request, fieldname, emailaddress, is_shortcode = False)
        if (not failure):
            # now build the email
            # ATTN: THESE VIEWFILES NEED FIXING
            failure = self.send_field_verification_email_given_verification(verification, fieldname, emailaddress)
        return failure



    def send_field_verification_email_given_verification(self, verification, fieldname, emailaddress):
        """Send a verification email."""
        emailtemplatefile = self.calc_account_templatepath(self.viewfiles['user_verify_field_email'])
        verificationurl = self.calc_verificationurl_field(verification, fieldname)
        maildict = {
            'to': [ emailaddress ],
            'subject': "E-mail address verification",
            'body': self.get_mewlosite().renderstr_from_template_file(emailtemplatefile, {'verificationurl':verificationurl})
        }
        # now send it
        failure = self.sitecomp_mailmanager().send_email(maildict)
        return failure




    def calc_account_templatepath(self, viewfilepath):
        """Template path inside user account site addon."""
        viewbasepath = '${addon_account_path}/views/'
        return viewbasepath+viewfilepath



    def build_userfield_verification(self, user, request, fieldname, fieldval, is_shortcode):
        """Build a verification entry for a user field.
        return tuple (verification, failure)"""

        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()

        # verification properties
        # ATTN:TODO - move some of this stuff to options and constants
        verification_type = mconst.DEF_VFTYPE_userfield_verification
        # set verification_varname for quick lookup
        verification_varname = fieldname
        verification_varval = fieldval
        # other values
        expiration_days = 14
        # the verification fields will contain the userdict so we can reinstate any values they provided at sign up time, when they confirm
        extradict = None

        # before we create a new verification entry, we *may* sometimes want to delete/invalidate previous verification requests of same type from same user/session
        # and matching the same fieldname
        verificationmanager.invalidate_previousverifications(verification_type, request, fieldname, "It was canceled due to a more recent request.")

        # create it via verificationmanager
        verification = verificationmanager.create_verification(verification_type)
        # set it's properties
        verification.init_values(request, expiration_days, verification_varname, verification_varval, extradict, is_shortcode, user)
        # save it
        verification.save()
        # return it
        return verification, None



    def cancel_userfield_verifications(self, user, request, fieldname, invalidreason):
        """Delete any previous field verification."""
        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()
        verification_type = mconst.DEF_VFTYPE_userfield_verification
        verificationmanager.invalidate_previousverifications(verification_type, request, fieldname, invalidreason)
        return None




    def calc_verificationurl_field(self, verification, fieldname):
        """The url user must visit to verify field change/initialization."""
        url = self.get_mewlosite().build_routeurl_byid('userfield_verify', flag_relative=False, args={'field':fieldname, 'code':verification.verification_code} )
        return url


















































    def login_user(self, userdict):
        """
        Make a new user account.
        return tuple (userobject, errordict)
        IMPORTANT: if there are errors return userobject as None (and set errordict)
        """
        errordict = {}
        # first find user by username or email
        user = self.find_user_by_dict(userdict)
        if (user == None):
            # ATTN:TODO -- what would be nice is if we checked pending verifications -- if we find the user, instead of saying "user could not be found" we can tell them they need to verify first and give them a link to resend, etc.
            errordict[mconst.DEF_FORM_GenericErrorKey] = "User could not be found."
            return None, errordict

        # check password
        password_plaintext = userdict['password']
        does_passwordmatch = user.does_plaintextpasswordmatch(password_plaintext)
        if (not does_passwordmatch):
            errordict['password'] = "Password does not match."
            return None, errordict

        # password matches -- they can be logged in
        # we will update the last login date; called must set session user
        user.update_date_lastlogin()
        # force any actions after they login? (we may want to do this if our hash password algorithm changes)
        user.actions_after_login()

        # return it
        return user, errordict




    def find_user_by_dict_with_field(self, userdict):
        """Lookup user by a uniquely identifiable field in userdict (typically username or email).
        We use this general function so that we can expand to support looking up by phone numbers, etc.
        We have a list of fields that we know uniquely identify users and we check EACH of these in turn (not the combo of them all); when we find a match we return the user and the fieldname that matched.
        It is called during login (to identify the user logging in) and during registration (to check if the username or email, etc. is already in use).
        Return tupe of (user, matchingfieldname)
        """
        user = None
        identifiablefields = {'username', 'email'}
        for fieldname in identifiablefields:
            if ( (fieldname in userdict) and (userdict[fieldname]!=None) and (userdict[fieldname]!='') ):
                keydict = {fieldname: userdict[fieldname]}
                user = self.modelclass.find_one_bykey(keydict)
                if (user != None):
                    return (user, fieldname)
        return None, None


    def find_user_by_dict(self, userdict):
        """Simple shortcut."""
        (user, matchingfield) = self.find_user_by_dict_with_field(userdict)
        return user



    def hash_and_salt_password(self, password_plaintext):
        """Return a hashed and salted version of the password, suitable for database storage."""
        password_hashed = misc.encode_hash_and_salt(password_plaintext)
        return password_hashed





    def error_if_user_exists(self, userdict):
        """Return a dictionary of fieldname:error if the user exists,
        Otherwise return {}."""

        # look up user
        (user, matchingfieldname) = self.find_user_by_dict_with_field(userdict)
        if (user != None):
            errordict = {matchingfieldname: "A user already exists with this {0}.".format(matchingfieldname)}
            return errordict
        # user not found, so that's good
        return {}
















    def set_userfield_from_verification(self, verification):
        """The user specified in the verification gets the new value, which is marked as verified."""
        # get userid, varname, varval
        userid = verification.user_id
        varname = verification.verification_varname
        varval = verification.verification_varval
        # lookup user
        user = self.finduser_byid(userid)
        if (user == None):
            # user not found
            return EFailure("User id#{0} not found.".format(userid))
        failure = self.check_uniquefield_notinuse(user, varname, varval)
        if (failure !=None):
            return failure
        # set it
        user.set_fieldvalue_with_verificationstate(varname, varval, verificationstate=True)
        # success
        return None



    def check_uniquefield_notinuse(self, user, fieldname, fieldval):
        """If fieldname is a field that must be unique to a user, make sure no other user has this field value."""
        if ((fieldname == 'email') or (fieldname == 'username')):
            duplicateuser = self.sitecomp_usermanager().find_user_by_dict({fieldname:fieldval})
            if ( (duplicateuser != None) and (duplicateuser!=user) ):
                return EFailure("Error: There is another user with that {0}.".format(fieldname))
        return None




    def finduser_byid(self, userid):
        """Just look up a user by their id."""
        user = self.modelclass.find_one_byprimaryid(userid)
        return user













    def build_generic_user_verification(self, verification_type, user, request, fieldname, fieldval, extradict, is_shortcode, flag_invalidateprevious):
        """Build a verification entry for a user field.
        return tuple (verification, failure)"""

        # get reference to the verification manager from the site
        verificationmanager = self.sitecomp_verificationmanager()

        # verification properties
        verification_varname = fieldname
        verification_varval = fieldval
        # other values
        expiration_days = 14

        # before we create a new verification entry, we *may* sometimes want to delete/invalidate previous verification requests of same type from same user/session
        if (flag_invalidateprevious):
            verificationmanager.invalidate_previousverifications(verification_type, request, fieldname, "It was canceled due to a more recent request.")

        # create it via verificationmanager
        verification = verificationmanager.create_verification(verification_type)
        # set it's properties
        verification.init_values(request, expiration_days, verification_varname, verification_varval, extradict, is_shortcode, user)
        # save it
        verification.save()
        # return it
        return verification, None