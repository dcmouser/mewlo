"""
dbmodel_settingsdict.py

This is our database object base class.

"""


# helper imports
import dbmodel
import dbfield

# python imports






class DbModel_SettingsDictionary(dbmodel.DbModel):
    """Database model where each row is a serialized dictioary setting."""

    # class variables
    dbtablename = 'settings'
    dbschemaname = 'default'



    def __init__(self):
        """Constructor."""
        # ATTN: NOTE THIS IS *NOT* CALLED WHEN INSTANTIATING MODELS VIA SQLALCHEMY ORM
        # parent function
        super(DbModel_SettingsDictionary,self).__init__()
        # init
        self.keyname = 'testkeyname'
        self.serializeddict = None




    def get_unserializeddict(self):
        """Unserialized the loaded key string."""
        serializedtext = self.serialized_dict
        if (serializedtext==None):
            return None
        return self.unserialize(serializedtext)

    def get_propertyname(self):
        print "DIR FOR DICTROW:"+str(self.__dict__)
        return self.keyname

    def storeserialize_dict(self, datadict):
        """Unserialized the loaded key string."""
        self.serialized_dict = self.serialize(datadict)



    @classmethod
    def definedb(cls):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list
        fields = [
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
        # now register fields
        cls.register_fields(fields)

