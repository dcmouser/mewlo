"""
mavatar.py
This module defines the MewloAvatar object which helps manage avatars for users (and potential for other entities like groups).
We have two aims for our avatar system:
    * Firstly, we want a flexible and robust avatar system that lets users upload images, link to external images, have automatic avatars, etc.
    * Secondly, we need to be able to access avatar information quickly and efficiently since user avatars may be ubiquitous.
So solve both of these, we adopt a semi-un-normalized database approach:
    * Avatars have their own database table to hold rich information.
    * User (and possibly) group objects hold a simple cached url for the user's avatar, suitable for most displays.
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..manager import manager
from ..helpers import misc
from ..uploads import muploads

# python imports






class MewloAvatar(mdbmodel.MewloDbModel):
    """The role class manages hierarchy of roles."""

    # class variables
    dbtablename = 'avatar'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),

            mdbmixins.dbfmixin_gobreference('owner', "The owning object gobid"),

            mdbfield.DbfTypeString('avatartype', {
                'label': "The type of avatar (file, url, service, etc.)"
                }),
            mdbfield.DbfLabelString('label', {
                'label': "The descriptive label for the avatar"
                }),

            mdbfield.Dbf1to1_OneWay('image_upload',  {
                'label': "Path to local file",
                'rightclass': muploads.MewloUpload,
                'relationname': 'uploadobject',
                }),

            mdbfield.DbfFilePathString('image_filepath', {
                'label': "Path to local file"
                }),
            mdbfield.DbfUrlPathString('image_urlpath', {
                'label': "Url of remote image"
                }),
            mdbfield.DbfString('avatar_service_code', {
                'label': "Code used by remote avatar service (gravatar md5, etc.)"
                }),

             ]

        # add disable/delete fields
        fieldlist += mdbmixins.dbfmixins_disabledelete()

        return fieldlist


