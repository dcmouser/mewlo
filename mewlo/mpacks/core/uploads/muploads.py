"""
muploads.py
This module defines the MewloUpload class which represents an uploaded file
"""


# mewlo imports
from ..database import mdbmodel
from ..database import mdbfield
from ..database import mdbmixins
from ..manager import manager
from ..helpers import misc

# python imports






class MewloUpload(mdbmodel.MewloDbModel):
    """A class that represents an uploaded file; could be an avatar image, a message attachment, a blog image, etc.."""

    # class variables
    dbtablename = 'upload'
    dbschemaname = 'default'

    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""

        # define fields list
        fieldlist = [

            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),

            mdbmixins.dbfmixin_gobreference('owner', "Owning user (user who uploaded the file"),

            mdbfield.DbfLabelString('label', {
                'label': "The descriptive label for the upload"
                }),
            mdbfield.DbfTypeString('uploadtype', {
                'label': "A short type string for the upload to help identify it"
                }),

            mdbfield.DbfFilePathString('filepath', {
                'label': "Path to local file"
                }),

            # sometimes we may automatically fetch and mirror an external file (image); if so we record the source url path here
            mdbfield.DbfUrlPathString('source_urlpath', {
                'label': "Url of remote image"
                }),

            mdbfield.DbfTimestamp('date_uploaded', {
                'label': "Date of upload"
                }),

            # an arbitrarily long string serializing any role properties that we don't have explicit fields for.
            mdbfield.DbfSerialized('serialized_fields', {
                'label': "The serialzed text version of any extra properties"
                }),
             ]

        fieldlist += mdbmixins.dbfmixins_disabledelete()

        return fieldlist


