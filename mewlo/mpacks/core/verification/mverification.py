"""
mverification.py
Database object for storing verification entries
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield

# python imports
import time
import uuid


class MewloVerification(mdbmodel.MewloDbModel):
    """Session object / database model."""

    # class variables
    dbtablename = 'verification'

    # verification types
    DEF_verificationtype_newuseraccount = 'NewUserAccount'
    DEF_verificationtype_uservarchange = 'UserVarChange'



    def __init__(self):
        """
        Constructor.
        Important: Dynamically/automatically created instance (eg by SqlAlchemy) do not get this call, if i am remembering correctly, so we can't depend on it.
        """
        self.init()

    def init(self):
        """Manually called init on manually created new instances."""
        pass





































    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list

        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id#"
                }),
            mdbfield.DbfCryptoHash('sessionhashkey', {
                'label': "Allow locking of the verification entry to a specific session id"
                }),
            mdbfield.DbfForeignUserId('user_id', {
                'label': "The user id owning this session"
                }),
            mdbfield.DbfTimestamp('date_created', {
                'label': "Date when verification entry was created"
                }),
            mdbfield.DbfTimestamp('date_expired', {
                'label': "Date when verification entry will expire"
                }),
            mdbfield.DbfTimestamp('date_consumed', {
                'label': "Date when verification entry was consumed"
                }),
            mdbfield.DbfTimestamp('failedattempt_count', {
                'label': "How many failed attempts have they made to match this verification code?"
                }),
            mdbfield.DbfServerIp('ip', {
                'label': "IP of user when verification was created"
                }),
            mdbfield.DbfTypeString('verification_type', {
                'label': "Type of verification"
                }),
            mdbfield.DbfBoolean('does_requirelogin', {
                'label': "Must user be logged in to trigger this verification (use with short codes)"
                }),
            mdbfield.DbfCryptoHash('verification_code', {
                'label': "Verification code user must provide"
                }),
            mdbfield.DbfVarname('verification_varname', {
                'label': "Variable name being verified"
                }),
            mdbfield.DbfTypeString('verification_varval', {
                'label': "Variable value being verified"
                }),
            # serialized (pickled) data - large text field storing arbitrary data
            mdbfield.DbfSerialized('verificationvars_serialized', {
                'label': "Arbitrary serialized verification vars"
                }),
            ]

        return fieldlist








