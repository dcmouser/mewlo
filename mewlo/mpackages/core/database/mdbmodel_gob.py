"""
mdbmodel_gob.py

This is a model that is a generic global object reference (resource); used for example in the permission system.

"""


# mewlo imports
import mdbmodel
import mdbfield

# python imports






class MewloDbModel_Gob(mdbmodel.MewloDbModel):
    """Database model that is a generic global object reference (resource); used for example in the permission system."""

    # class variables
    dbtablename = 'gob'
    dbschemaname = 'default'



    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this item"
                }),
            # an arbitrarily long string serializing any other log properties that we don't have explicit fields for.
            mdbfield.DbfTypeString('objecttype', {
                'label': "The object type reffered to, as a string"
                }),
            # do we want to have a non-normalized (redundant) reference to the source object, even if we can't foreignkey it since it may be used for dif types
            mdbfield.DbfInteger('objectid', {
                'label': "The object id"
                }),
            ]

        cls.hash_fieldlist(fieldlist)

