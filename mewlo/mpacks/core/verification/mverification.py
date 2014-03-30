"""
mverification.py
Database object for storing verification entries
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..eventlog.mevent import EFailure, EException
from ..helpers import misc

# python imports
import uuid


class MewloVerification(mdbmodel.MewloDbModel):
    """Verification object / database model, used when user has set/changed a profile field that needs to be verified before being accepted."""

    # class variables
    dbtablename = 'verification'




    def __init__(self):
        """
        Constructor.
        Important: Dynamically/automatically created instance (eg by SqlAlchemy) do not get this call, if i am remembering correctly, so we can't depend on it.
        """
        self.init()

    def init(self):
        """Manually called init on manually created new instances."""
        pass







    def init_values(self, request, expiration_days, verification_varname, verification_varval, extradict, is_shortcode, user):
        """Set some values."""
        # set main values
        self.verification_code = self.make_randomverificationcode()
        # other calues
        self.is_shortcode = is_shortcode
        self.verification_varname = verification_varname
        self.verification_varval = verification_varval
        # set the entire contents of the serialized verification vars
        if (extradict != None):
            self.setdict_serialized('verificationvars_serialized',extradict)
        # set request-based values
        self.setvals_fromequest(request, user)
        # initial values
        self.date_created = misc.get_dbnowtime()
        self.date_expires = self.date_created + (expiration_days*60*60*24)
        self.failurecount = 0





    def setvals_fromequest(self, request, user):
        """Set some verification values from a request"""
        session = request.get_session(True)
        self.session_id = session.getid_saveifneeded()
        self.ip_created = session.ip
        if (user != None):
            self.user_id = user.id
        else:
            # should we grab it from session?
            #self.user_id = session.user_id
            pass



    def make_randomverificationcode(self):
        """Make a random secure unique verification code and return it.
        ATTN: at some point we will want to support long + short codes (see docs)."""
        return str(uuid.uuid4())


    def get_userdict(self):
        return self.getfield_serialized('verificationvars_serialized','userdict',{})





    def consume(self, request):
        """Mark verification entry as consumed/used successfully."""
        self.date_consumed = misc.get_dbnowtime()
        # add sessionip
        session = request.get_session(False)
        if (session != None):
            self.ip_consumed = session.ip
        # save it
        self.save()



    def increase_failurecount(self):
        """Increase the failure counter, and fail it iff too many.
        Return EFailure reason if too many failures; otherwise None
        """
        # increase failure count
        self.failurecount += 1
        self.save()
        # check if too many
        max_failures_allowed = 5
        if (self.failurecount > max_failures_allowed):
            invalidreason = "Incorrect code attempted too many times."
            self.set_invalid(invalidreason)
            return EFailure(invalidreason)
        self.save()
        return None


    def set_invalid(self, invalidreason):
        """Mark it as invalid."""
        self.incalidreason = invalidreason
        self.save()


    def update_dict_defaults_with_userdict(self, overidedict, forcelist = []):
        """Return a dictionary where userdict values are treated as defaults with overidedict merged after."""
        verifcation_userdict = self.get_userdict()
        for key,val in verifcation_userdict.iteritems():
            if ((key not in overidedict) or (key in forcelist)):
                overidedict[key]=val
        return overidedict











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








