"""
mbridge.py
This module defines the MewloBridge class which handled bridged logins (facebook, twitter, google, etc.)
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..manager import manager
from ..helpers import misc

# python imports






class MewloBridge(mdbmodel.MewloDbModel):
    """The MewloBridge class manages bridged logins."""

    # class variables
    dbtablename = 'bridge'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),

            mdbmixins.dbfmixin_gobreference('owner', "The owning user gobid"),

            mdbfield.DbfTypeString('bridge_type', {
                'label': "The type of bridge (service name, etc.)"
                }),
            mdbfield.DbfString('bridge_address', {
                'label': "Specific address (url) for the bridge, if needed"
                }),

            mdbfield.DbfLabelString('label', {
                'label': "The descriptive label for the bridge"
                }),

            # an arbitrarily long string serializing any other log properties that we don't have explicit fields for.
            mdbfield.DbfSerialized('extrafields_serialized', {
                'label': "Arbitrary dictionary of extra fields"
                }),
             ]

        # add some use fields (date and ip)
        fieldlist += mdbmixins.dbfmixins_dateipuse()

        # add disable/delete fields
        fieldlist += mdbmixins.dbfmixins_disabledelete()

        return fieldlist


