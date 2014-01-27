"""
mdbmodel_settings.py

This is our database object base class.

"""


# helper imports
import mdbmodel
import mdbfield

# python imports






class MewloDbModel_Settings(mdbmodel.MewloDbModel):
    """Database model where each row is a serialized dictioary setting."""

    # class variables
    dbtablename = 'settings'
    dbschemaname = 'default'


    def __init__(self):
        """Init on manual construct of object."""
        self.settingdict_serialized = None



    def get_settingdict_unserialized(self):
        """Unserialized the loaded key string."""
        return self.unserialize_fromstorage(self.settingdict_serialized,None)


    def set_settingdict_serialize(self, datadict):
        """Unserialized the loaded key string."""
        self.settingdict_serialized = self.serialize_forstorage(datadict)












    @classmethod
    def define_fields(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # a unique short text keyname
            mdbfield.DbfUniqueKeyname('keyname', {
                'label': "The unique key name for this group of properties"
                }),
            # an arbitrarily long string serializing a dictionary or array, etc.
            mdbfield.DbfSerialized('settingdict_serialized', {
                'label': "The serialzed text version of the dictionary/array data being stored"
                })
            ]
        return fieldlist

