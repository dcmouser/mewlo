"""
muser.py

This model represents users.

"""



# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..database import mdbmodel_fieldset
from ..helpers import misc

# python imports
import time



class MewloUser(mdbmodel.MewloDbModel):
    """User object / database model."""

    # class variables
    dbtablename = 'user'
    #
    flag_mixin_atroot = False


    def __init__(self):
        self.init()

    def init(self):
        """Manually called init on manually created new instances."""
        # IMPORTANT: create a new gob database model entry for this object
        self.gobify()


    def dumps(self, indent=0):
        outstr = " "*indent + "User reporting in:\n"
        indent += 1
        outstr += " "*indent + "username: {0}.\n".format(self.username)
        outstr += " "*indent + "id: {0}.\n".format(self.id)
        outstr += " "*indent + "email: {0}.\n".format(self.email)
        outstr += " "*indent + "password_hashed: {0}.\n".format(self.password_hashed)
        outstr += " "*indent + "date_lastlogin: {0}.\n".format(time.ctime(self.date_lastlogin))
        return outstr



    def update_date_lastlogin(self):
        """Update date of last login."""
        self.date_lastlogin = time.time()
        # ATTN: should we save now or autosave at end of requests
        # ATTN: TODO autosave user at end of request
        self.save()



    def does_plaintextpasswordmatch(self, plaintextpassword):
        """Return true if the plaintext password is a match for our stored hashed password."""
        return misc.does_plaintext_rehash(plaintextpassword, self.password_hashed)


    def actions_after_login(self):
        """If there are any actions we want to do after every login, this is where to do that."""
        self.upgrade_passwordhash_ifneeded()

    def upgrade_passwordhash_ifneeded(self):
        """Here we can check their hashed stored password, and if we have upgraded password algorithms since theirs, we could regenerated it and save it."""
        # ATTN: Unfinished
        return False










    def get_isloggedin(self):
        """Return true if this is a real user logged in, and not guest account, etc."""
        # ATTN: todo improve this
        return ((self.id != None) and (self.id>0))

    def get_username(self):
        """Accessor."""
        return self.username








    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list

        # ATTN: UNFINISHED
        fieldlist = [
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this user"
                }),
            mdbfield.DbfUsername('username', {
                'label': "The user's username"
                }),
            mdbfield.DbfEmail('email', {
                'label': "The user's email"
                }),
            mdbfield.DbfHashedPassword('password_hashed', {
                'label': "The hashed and salted password for the user"
                }),
            mdbfield.DbfTimestamp('date_lastlogin', {
                'date_lastlogin': "The date of the last login"
                }),
            # globally unique resource reference
            mdbmixins.dbfmixin_gobselfreference(),
            ]

        return fieldlist







    @classmethod
    def create_prerequisites(cls, dbmanager):
        """Create and register with the dbmanager any prerequisite stuff that this class uses."""
        subfields = mdbmixins.dbfmixins_authortracker()
        if (cls.flag_mixin_atroot):
            # prepare extra fields that will be added at root; this doesnt actually create any prerequisites
            cls.extend_fields(subfields)
        else:
            # add a special sub table that will contain some fields, using a helper class object attached to us
            # create (AND REGISTER) the new helper object
            mdbmodel_fieldset.MewloDbFieldset.make_fieldset_dbobjectclass(cls,'tracking','author tracking object',cls.dbtablename,dbmanager,subfields)





    @classmethod
    def getmake_guestuserobject(cls):
        """
        Make a guest user object and return it.
        Ultimately I think that "making" a guest user object, should probably involve loading a specific guest user account from database.
        ATTN: unfinished.
        """
        # ATTN: test -- for now just return a new object
        user = MewloUserTemp()
        return user


    @classmethod
    def create_user(cls, username, password_plaintext, email):
        """
        Make a new user account.
        return tuple (userobject, errordict); if there are errors return them and userobject as None
        """
        errordict = {}

        # make sure username and email are unique; error if not
        user = cls.find_user_by_username_or_email(username,email)
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
        user = MewloUser()
        user.username = username
        user.email = email
        user.password_hashed = cls.hash_and_salt_password(password_plaintext)
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




    @classmethod
    def login_user(cls, username=None, password_plaintext=None, email=None):
        """
        Make a new user account.
        return tuple (userobject, errordict)
        IMPORTANT: if there are errors return userobject as None (and set errordict)
        """
        errordict = {}
        # first find user by username or email
        user = cls.find_user_by_username_or_email(username,email)
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


    @classmethod
    def find_user_by_username_or_email(cls, username, email):
        """Lookup user by username or email; both of which may be set to None to ignore."""
        user = None
        if ((username != None) and (username != '')):
            # find by name
            keydict = {'username':username}
            user = MewloUser.find_one_bykey(keydict)
        if ((user == None) and (email != None) and (email!='')):
            # find by email
            keydict = {'email':email}
            user = MewloUser.find_one_bykey(keydict)
        return user



    @classmethod
    def hash_and_salt_password(cls, password_plaintext):
        """Return a hashed and salted version of the password, suitable for database storage."""
        password_hashed = misc.encode_hash_and_salt(password_plaintext)
        return password_hashed











class MewloUserTemp(MewloUser):
    """Derived from MewloUser but won't save to db."""


    def __init__(self):
        self.init()

    def init(self):
        """Manually called init on manually created new instances."""
        self.username = 'Guest'

    def save(self):
        """Raise exception if we try to save temp user."""
        raise Exception('Programming error: Cannot save MewloUserTemp users (usually created for guest account.')


    def get_isloggedin(self):
        """Return true if this is a real user logged in, and not guest account, etc."""
        return False




