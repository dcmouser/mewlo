"""
dbmodel_settings.py

This is our database object base class.

"""


# helper imports
import dbmodel
import dbfield

# python imports






class DbModel_Settings(dbmodel.DbModel):
    """Database model where each row is a serialized dictioary setting."""

    # class variables
    dbtablename = 'settings'
    dbschemaname = 'default'


    # ATTN: NOTE __INIT__ IS *NOT* CALLED WHEN INSTANTIATING MODELS VIA SQLALCHEMY ORM SO WE AVOID IT WHERE POSSIBLE
#    def __init__(self):
#        """Constructor."""
#        # init
#        self.keyname = None
#        self.serializeddict = None




    def get_unserialized_dict(self):
        """Unserialized the loaded key string."""
        serializedtext = self.serialized_dict
        if (serializedtext==None):
            return None
        return self.unserialize(serializedtext)


    def store_serialize_dict(self, datadict):
        """Unserialized the loaded key string."""
        self.serialized_dict = self.serialize(datadict)












    @classmethod
    def definedb(cls):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list
        cls.fields = [
            # standard primary id number field
            dbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # a unique short text keyname
            dbfield.DbfUniqueKeyname('keyname', {
                'label': "The unique key name for this group of properties"
                }),
            # an arbitrarily long string serializing a dictionary or array, etc.
            dbfield.DbfSerialized('serialized_dict', {
                'label': "The serialzed text version of the dictionary/array data being stored"
                })
            ]


