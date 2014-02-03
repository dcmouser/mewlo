"""
msession.py
Database object for storing session data
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..user import muser

# python imports
import time
import uuid


class MewloSession(mdbmodel.MewloDbModel):
    """Session object / database model."""

    # class variables
    dbtablename = 'session'

    def __init__(self):
        """
        Constructor.
        Important: Dynamically/automatically created instance (eg by SqlAlchemy) do not get this call, if i am remembering correctly, so we can't depend on it.
        """
        self.init()

    def init(self):
        """Manually called init on manually created new instances."""
        pass






    # serialized field accessor helpers
    def get_sessionvar(self, keyname, defaultval):
        return self.getfield_serialized('sessionvars_serialized', keyname, defaultval)
    def set_sessionvar(self, keyname, val):
        return self.setfield_serialized('sessionvars_serialized', keyname, val)



    # helper accessors
    def set_sessionmanager(self, sessionmanager):
        """Store session manager."""
        self.sessionmanager = sessionmanager

    def sitecomp_usermanager(self):
        """Get the user manager, from the session manager."""
        return self.sessionmanager.sitecomp_usermanager()


    def init_values(self, ip):
        """Set values for a new session."""
        curtime = time.time()
        self.date_create = curtime
        self.date_update = curtime
        self.date_access = curtime
        self.ip = ip
        self.user_id = None
        self.set_randomhashkey()
        self.set_isdirty(True)


    def set_randomhashkey(self):
        """Set a random hashkey for the session.
        This is slightly awkward since we would really like to keep the session function generator in the MewloSessionManager class.
        But then we don't know how to invoke that here since a session doesn't get a reference to the helper (we could change that).
        ATTN: UNFINISHED.
        """
        sessionhashkey = str(self.create_unique_sessionhashkey())
        self.hashkey = sessionhashkey
        self.set_isdirty(True)


    def update_access(self):
        """Update access time."""
        curtime = time.time()
        self.date_access = curtime
        self.set_isdirty(True)


    def set_user(self, userobject):
        """
        Set the user for a session.
        This may happen after a login, or after a guest user account is set up for a visitor.
        There is one important security concern we should be aware of:
        We may want to force a change of the session id any time the user identity changes from one user to another.
        That would prevent a client from tricking another client to use their session id and then login, essentially upgrading the previous session id user.
        """
        # assign new user object
        self.user = userobject
        if (userobject == None):
            self.user_id = None
        else:
            # ok it's a valid user object
            if (self.user_id != None and self.user_id != userobject.id):
                # we are CHANGING the user associated with this session, so for a new random sessionid
                self.set_randomhashkey()
            # assign new user id
            if (userobject.id == None):
                # userobject is valid but it has no id, that just means it hasn't been saved yet
                raise Exception("User object not saved yet.")
            self.user_id = userobject.id
        self.set_isdirty(True)



    # lazy user requester object creation
    def get_user(self, flag_makeuserifnone):
        """Lazy return the user OBJECT associated with this session."""
        # ATTN: why are we setting self.user directly in first half of this function, but called set_user in second half which is a fully involved function call;
        # is it because in later case its a new object just being created which needs its self.user_id set
        if (not hasattr(self,'user')):
            # it's not yet cached, so find user and cache
            if (self.user_id == None):
                # no user
                self.user = None
            else:
                # we need to load it
                self.user = self.sitecomp_usermanager().modelclass.find_one_byprimaryid(self.user_id, None)
        # no user object? should we make a GUEST one?
        if (self.user == None and flag_makeuserifnone):
            # ok we want to "make" a user object (which may just mean loading GUEST user object from db); and then remember to set self.user and self.user_id
            user = self.sitecomp_usermanager().getmake_guestuserobject()
            self.set_user(user)
        # return it
        return self.user



    def create_unique_sessionhashkey(self):
        """Create a new unique session hashkey."""
        sessionid = uuid.uuid4()
        return sessionid






















    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list

        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this user"
                }),
            # hashid - the unique string stored in user cookie that we use to lookup stuff (needs index)
            mdbfield.DbfCryptoHash('hashkey', {
                'label': "The unique hash key for this session"
                }),
            # userid - quick user id field - so we might avoid unserialized large data for the most common things
            mdbfield.DbfForeignUserId('user_id', {
                'label': "The user id owning this session"
                }),
            # date fields
            mdbfield.DbfTimestamp('date_create', {
                'label': "Date when session was created"
                }),
            mdbfield.DbfTimestamp('date_update', {
                'label': "Date when session was last modified"
                }),
            mdbfield.DbfTimestamp('date_access', {
                'label': "Date when session was last accessed (read)"
                }),
            # ip - for increased security checking
            mdbfield.DbfServerIp('ip', {
                'label': "IP of user when session was created"
                }),
            # serialized (pickled) data - large text field storing arbitrary data
            mdbfield.DbfSerialized('sessionvars_serialized', {
                'label': "Arbitrary serialized session vars"
                }),
            ]

        return fieldlist









