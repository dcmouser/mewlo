"""
msession.py
Database object for storing session data
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield



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
                'label': "Date when session was last accessed (read)"
                }),
            # serialized (pickled) data - large text field storing arbitrary data
            mdbfield.DbfSerialized('sessionvars_serialized', {
                'label': "Arbitrary serialized session vars"
                }),
            ]

        return fieldlist









