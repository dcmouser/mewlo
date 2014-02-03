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



    def create_user(self, username, password_plaintext, email):
        """
        Make a new user account.
        return tuple (userobject, errordict); if there are errors return them and userobject as None
        """
        errordict = {}

        # make sure username and email are unique; error if not
        user = self.find_user_by_username_or_email(username,email)
        if (user != None):
            # error, user already exists, let's tell them
            if ((user.username != None) and (user.username == username) and (user.email != None) and (user.email == email)):
                errordict[''] = 'A user with this username and email already exists.'
            if ((user.username != None) and (user.username == username) ):
                errordict['username'] = 'Username already in use.'
            if ((user.email != None) and (user.email == email) ):
                errordict['email'] = 'Email already in use.'
            return None, errordict

        # create user account.
        user = self.modelclass()
        user.username = username
        user.email = email
        user.password_hashed = self.hash_and_salt_password(password_plaintext)
        # assuming no errors, save it
        if (len(errordict)==0):
            # no errors, save it
            user.save()
        # check again for errors (this allows us to handle save errors eventually)
        if (len(errordict)>0):
            # errors, clear user object
            user = None
        # return it
        return user, errordict



    def login_user(self, username=None, password_plaintext=None, email=None):
        """
        Make a new user account.
        return tuple (userobject, errordict)
        IMPORTANT: if there are errors return userobject as None (and set errordict)
        """
        errordict = {}
        # first find user by username or email
        user = self.find_user_by_username_or_email(username,email)
        if (user == None):
            if ((username != None) and (email != None)):
                errordict[''] = "No user exists with that username or email."
            elif (email != None):
                errordict['email'] = "No user exists with that email."
            else:
                errordict['username'] = "No user exists with that username."
            return None, errordict

        # check password
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



    def find_user_by_username_or_email(self, username, email):
        """Lookup user by username or email; both of which may be set to None to ignore."""
        user = None
        if ((username != None) and (username != '')):
            # find by name
            keydict = {'username':username}
            user = self.modelclass.find_one_bykey(keydict)
        if ((user == None) and (email != None) and (email!='')):
            # find by email
            keydict = {'email':email}
            user = self.modelclass.find_one_bykey(keydict)
        return user



    def hash_and_salt_password(self, password_plaintext):
        """Return a hashed and salted version of the password, suitable for database storage."""
        password_hashed = misc.encode_hash_and_salt(password_plaintext)
        return password_hashed





