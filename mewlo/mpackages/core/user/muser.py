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

    def upgrade_passwordhash_ifneeded(self):
        """Here we can check their hashed stored password, and if we have upgraded password algorithms since theirs, we could regenerated it and save it."""
        # ATTN: Unfinished
        return False






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
        user = MewloUser()
        user.username = 'Guest'
        return user


    @classmethod
    def create_user(cls, username, password_plaintext, email):
        """
        Make a new user account.
        return tuple (userobject, errordict); if there are errors return them and userobject as None
        """
        errordict = {}
        # ATTN: test -- for now just return a new object
        # create user account.
        user = MewloUser()
        user.username = username
        user.email = email
        user.password_hashed = cls.hash_and_salt_password(password_plaintext)
        # assuming no errors, save it
        if (len(errordict)==0):
            # no errors, save it
            user.save()
            # and force a flush right now so that it's id is accessible right away
            user.flush_toupdate()
            print "ATTN: New user has been created and now saved:"
            print user.dumps()
        # check again for errors (this allows us to handle save errors eventually)
        if (len(errordict)>0):
            # errors, clear user object
            user = None
        # return it
        return user, errordict


    @classmethod
    def login_user(cls, username, password_plaintext):
        """
        Make a new user account.
        return tuple (userobject, errordict); if there are errors return them and userobject as None
        """
        errordict = {}
        # first find user by username
        keydict = {'username':username}
        user = MewloUser.find_one_bykey(keydict,None)
        if (user == None):
            errordict['username'] = "Username does not exist."
        else:
            # check password
            does_passwordmatch = user.does_plaintextpasswordmatch(password_plaintext)
            if (not does_passwordmatch):
                errordict['password'] = "Password does not match."
            else:
                # password matches -- they can be logged in
                # we will update the last login date; called must set session user
                user.update_date_lastlogin()
                # force upgradre of hashed stored password? (we may want to do this if our hash password algorithm changes)
                user.upgrade_passwordhash_ifneeded()
                # ATTN: note this doesn't save user model; we have to make sure we add that later or have an auto save on request end

        # return it
        return user, errordict





    @classmethod
    def hash_and_salt_password(cls, password_plaintext):
        """Return a hashed and salted version of the password, suitable for database storage."""
        password_hashed = misc.encode_hash_and_salt(password_plaintext)
        return password_hashed





