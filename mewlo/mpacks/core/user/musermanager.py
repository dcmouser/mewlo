"""
musermanager.py

The helper manager for user model.

"""



# mewlo imports
from ..manager import modelmanager
from ..helpers import misc
import muser

# python imports





class MewloUserManager(modelmanager.MewloModelManager):
    """User model manager."""

    def __init__(self, mewlosite, debugmode):
        # parent constructor -- pass in the main modelclass we manager
        super(MewloUserManager,self).__init__(mewlosite, debugmode, muser.MewloUser)
        # also keep track of temp user
        self.modelclass_tempuser = muser.MewloUserTemp

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



    def create_user(self, userdict, verifiedfields):
        """
        Make a new user account.
        We take a userdict instead of explicit variables for username, email, password, so that we can eventually accomodate whatever initial user properties we have specified at time of registration.
        return tuple (userobject, errordict); if there are errors return them and userobject as None
        """
        errordict = {}

        # make sure unique fields (username, email) are unique; error if not
        errordict = self.error_if_user_exists(userdict)
        if (len(errordict)>0): 
            return None, errordict, ''

        # create user account.
        user = self.modelclass()
        user.username = userdict['username']
        user.email = userdict['email']
        user.password_hashed = self.hash_and_salt_password(userdict['password'])
        

        # ATTN:TODO handle verifiedfields -- if email not verified we should send them an email to verify it
        # ATTN:TODO track whether email (etc.) is verified

        
        # assuming no errors, save it
        if (len(errordict)==0):
            # no errors, save it
            user.save()
        # check again for errors (this allows us to handle save errors eventually)
        if (len(errordict)>0):
            # errors, clear user object
            user = None
        #
        successmessage = 'User account has been successfully created.'
        # return it
        return user, errordict, successmessage



    def login_user(self, userdict):
        """
        Make a new user account.
        return tuple (userobject, errordict)
        IMPORTANT: if there are errors return userobject as None (and set errordict)
        """
        errordict = {}
        # first find user by username or email
        (user, matchingfield) = self.find_user_by_dict(userdict)
        if (user == None):
            # ATTN:TODO -- what would be nice is if we checked pending verifications -- if we find the user, instead of saying "user could not be found" we can tell them they need to verify first and give them a link to resend, etc.
            errordict[''] = "User could not be found."
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




    def find_user_by_dict(self, userdict):
        """Lookup user by a uniquely identifiable field in userdict (typically username or email).
        We use this general function so that we can expand to support looking up by phone numbers, etc.
        We have a list of fields that we know uniquely identify users and we check EACH of these in turn (not the combo of them all); when we find a match we return the user and the fieldname that matched.
        It is called during login (to identify the user logging in) and during registration (to check if the username or email, etc. is already in use).
        Return tupe of (user, matchingfieldname)
        """
        user = None
        identifiablefields = {'username', 'email'}
        for fieldname in identifiablefields:
            if ((fieldname in userdict) and (userdict[fieldname]!=None) and (userdict[fieldname]!='')):
                keydict = {fieldname: userdict[fieldname]}
                user = self.modelclass.find_one_bykey(keydict)
                if (user!=None):
                    return (user, fieldname)
        return None, None



    def hash_and_salt_password(self, password_plaintext):
        """Return a hashed and salted version of the password, suitable for database storage."""
        password_hashed = misc.encode_hash_and_salt(password_plaintext)
        return password_hashed





    def error_if_user_exists(self, userdict):
        """Return a dictionary of fieldname:error if the user exists,
        Otherwise return {}."""
        
        # look up user
        (user, matchingfieldname) = self.find_user_by_dict(userdict)
        if (user != None):
            errordict = {matchingfieldname: "A user already exists with this {0}.".format(matchingfieldname)}
            return errordict
        # user not found, so that's good
        return {}
















