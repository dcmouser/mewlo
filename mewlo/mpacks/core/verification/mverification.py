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







    def init_values(self, request, expiration_days, verification_varname=None, verification_varval=None, extradict={}, is_shortcode=False):
        """Set some values."""
        # set main values
        self.verification_code = self.make_randomverificationcode()
        # other calues
        self.is_shortcode = is_shortcode        
        self.verification_varname = verification_varname
        self.verification_varval = verification_varval
        # set the entire contents of the serialized verification vars
        self.setdict_serialized('verificationvars_serialized',extradict)
        # set request-based values
        self.setvals_fromequest(request)
        # initial values
        self.date_created = self.get_nowtime()        
        self.date_expires = self.date_created + expiration_days
        self.failurecount = 0





    def setvals_fromequest(self, request):
        """Set some verification values from a request"""
        session = request.get_session(True)  
        self.session_id = session.getid_saveifneeded()
        self.ip_created = session.ip
        self.user_id = session.user_id



    def make_randomverificationcode(self):
        """Make a random secure unique verification code and return it.
        ATTN: at some point we will want to support long + short codes (see docs)."""
        return str(uuid.uuid4())


    def get_userdict(self):
        return self.getfield_serialized('verificationvars_serialized','userdict',{})





    def consume(self, request):
        """Mark verification entry as consumed/used successfully."""
        self.date_consumed = self.get_nowtime()
        # add sessionip
        session = request.get_session(False)
        if (session != None):            
            self.ip_consumed = session.ip
        # save it
        self.save()


        
    def increment_failurecount(self):
        """Increase the failure counter, and fail it iff too many."""
        self.failurecount += 1
        max_failures_allowed = 10
        if (self.failurecount > max_failures_allowed):
            self.set_invalid("Too many failed attempts to enter code.")
        else:
            self.save()
            
    def set_invalid(self, invalidreason):
        """Mark it as invalid."""
        self.incalidreason = invalidreason
        self.save()













    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list

        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id#"
                }),
            mdbfield.DbfString('invalidreason', {
                'label': "Reason it's being marked as invalid?"
                }),
            mdbfield.DbfInteger('failurecount', {
                'label': "Number of times the user has failed to match this code (used for short codes)"
                }),
            mdbfield.DbfInteger('session_id', {
                'label': "Allow locking of the verification entry to a specific session id"
                }),
            mdbfield.DbfForeignUserId('user_id', {
                'label': "The user id owning this session"
                }),
            mdbfield.DbfTimestamp('date_created', {
                'label': "Date when verification entry was created"
                }),
            mdbfield.DbfTimestamp('date_expires', {
                'label': "Date when verification entry will expire"
                }),
            mdbfield.DbfTimestamp('date_consumed', {
                'label': "Date when verification entry was consumed"
                }),
            mdbfield.DbfServerIp('ip_created', {
                'label': "IP of user when verification was created"
                }),
            mdbfield.DbfServerIp('ip_consumed', {
                'label': "IP of user when verification was consumed"
                }),
            mdbfield.DbfTypeString('verification_type', {
                'label': "Type of verification"
                }),
            mdbfield.DbfBoolean('is_shortcode', {
                'label': "Short codes cannot be matched without also matching against user session or userid"
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








