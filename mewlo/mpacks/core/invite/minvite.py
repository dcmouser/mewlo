"""
minvite.py
For invitations (typically to join a group)
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..manager import manager
from ..helpers import misc
from ..uploads import muploads

# python imports






class MewloInvitation(mdbmodel.MewloDbModel):
    """Manages invites."""

    # class variables
    dbtablename = 'invitation'
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

            mdbmixins.dbfmixin_gobreference('inviter',"The user doing the inviting"),
            mdbmixins.dbfmixin_gobreference('invitee',"The user being invited"),
            mdbmixins.dbfmixin_gobreference('resoure',"A resource which is being offered"),

            mdbfield.DbfTypeString('invitation_type', {
                'label': "The type of invitation"
                }),

            mdbfield.DbfLabelString('invitation_message', {
                'label': "Text message associated with the invitation"
                }),


            mdbfield.DbfTimestamp('date_invitation', {
                'label': "Date of invitation",
                }),
            mdbfield.DbfTimestamp('date_acceptance', {
                'label': "Date of acceptance",
                }),

             ]

        fieldlist += mdbmixins.dbfmixins_disabledelete()

        return fieldlist



