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
from ..constants.mconstants import MewloConstants as mconst


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

    def get_date_lastlogin(self):
        return self.get_date_lastlogin

    def has_recently_loggedin(self, recentminutes):
        """Return true if they have logged in (or provided password) in last recentminutes minutes."""
        timesincelogin_secs = time.time() - self.date_lastlogin
        return timesincelogin_secs < recentminutes * 60


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








    def get_email_htmlinfo(self, request):
        """
        Return an html string that describes their email and email status.
        For example:  mouser@donationcoder.com (verified).
        or: mouser@donationcoder.com (not yet verified; <a href="">resend verification email</a>).
        or mouser@donationcoder.com, pending change to mouser2@dcmembers.org (<a href="">resend confirmation email</a> or <a href="">cancel change</a>).
        or no email address provided (provide one now).
        """

        if ((self.email == None) or (self.email == '')):
            # there is no email address on file at all
            rethtml = "No email address provided (" + "provide one now" +")."
        else:
            rethtml = self.email
            # we have one, now is it verified?
            if (self.isverified_email):
                rethtml += " (verified)"
            else:
                rethtml += " (not yet verified)"
            # now let's check for pending change to their email
            verification = request.sitecomp_verificationmanager().find_valid_by_type_and_userid(mconst.DEF_VFTYPE_userfield_verification, self.id, 'email')
            if (verification != None):
                rethtml += " [pending change to {0}]".format(verification.verification_varval)

        # return it
        return rethtml










    def set_fieldvalue_with_verificationstate(self, varname, varval, verificationstate):
        """Set value of a field and makring it as verified."""
        # special cases
        if (varname == 'email'):
            self.email = varval
            self.isverified_email = verificationstate
        else:
            # other cases
            raise Exception("We don't know how to set fieldvalue for {0}.".format(varname))








    def get_fieldvalue_and_verificationstatus(self, fieldname):
        """Return tuple (fieldvalue, isverified) for this field."""
        # ATTN: unfinished
        if (fieldname == 'email'):
            return (self.email, self.isverified_email)
        # unknown
        raise Exception("Do not know how to get value for field {0}.".format(fieldname))




    def getfield_byname(self, fieldname, defaultval = None):
        """Accessor."""
        if (hasattr(self, fieldname)):
            return getattr(self, fieldname)
        return defaultval



    def is_safe_stranger_claim_thisaccount(self):
        """This is called if someone claims to have entered the wrong email after just creating an account; return True if we want to let them change the email address of this account.
        We should only allow this on accounts which have never been logged into or had anything done with.
        Allowing this makes it much easier for someone who provides a bad email at signup to fix it.
        """
        # It's safe to claim if its a new account that hasn't yet been verified
        return self.get_ispending_newuser_verification()




    def get_ispending_newuser_verification(self):
        """Is this user account pending a newuser verification?"""
        return not self.isverified_email


    def get_ispending_fieldmodify_verification(self, request):
        """Is this user account pending a field modificationverification?"""
        verification = request.sitecomp_verificationmanager().find_valid_by_type_and_userid(mconst.DEF_VFTYPE_userfield_verification, self.id, None)
        return (verification != None)




























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
            mdbfield.DbfBoolean('isverified_email', {
                'label': "Is the user's email verified?"
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
            backrefname = cls.get_dbtablename_pure()
            mdbmodel_fieldset.MewloDbFieldset.make_fieldset_dbobjectclass(cls,'tracking','author tracking object',backrefname,dbmanager,subfields)






















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




