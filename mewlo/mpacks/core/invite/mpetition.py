"""
mpetition.py
For petitions (typically to join a group)
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..manager import manager
from ..helpers import misc
from ..uploads import muploads

# python imports









class MewloPetition(mdbmodel.MewloDbModel):
    """Manages invites."""

    # class variables
    dbtablename = 'petition'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),

            mdbmixins.dbfmixin_gobreference('applicant', "The user who is petitioning for some permission (usually to join a group)"),
            mdbmixins.dbfmixin_gobreference('resoure', "The resource being petitioned for (optional)"),

            mdbfield.DbfTypeString('petition_type', {
                'label': "The type of petition"
                }),

            mdbfield.DbfLabelString('petition_message', {
                'label': "Text message associated with the petition"
                }),


            mdbfield.DbfTimestamp('date_petition', {
                'label': "Date of invitation",
                }),
            mdbfield.DbfTimestamp('date_acceptance', {
                'label': "Date of acceptance",
                }),

             ]

        # add disable/delete fields
        fieldlist += mdbmixins.dbfmixins_disabledelete()

        return fieldlist




