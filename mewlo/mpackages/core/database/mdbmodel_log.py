"""
mdbmodel_log.py

This is a base class for logging to database.
Subclasses can add new fields.

"""


# mewlo imports
import mdbmodel
import mdbfield

# python imports






class MewloDbModel_Log(mdbmodel.MewloDbModel):
    """Database model where each row is a serialized dictioary setting."""

    # class variables
    dbtablename = 'log'
    dbschemaname = 'default'
    # log fields to ignore
    ignored_logfields = []



    # ATTN: NOTE __INIT__ IS *NOT* CALLED WHEN INSTANTIATING MODELS VIA SQLALCHEMY ORM SO WE AVOID IT WHERE POSSIBLE



    def get_unserialized_fields(self):
        """Unserialized the string property."""
        serializedtext = self.serialized_fields
        if (serializedtext==None):
            return None
        return self.unserialize(serializedtext)


    def store_serialize_fields(self, fields):
        """Serialize an object into the serialized_fields property."""
        self.serialized_fields = self.serialize(fields)


    def set_property_byname(self, propname, propval):
        """Set an object property by name."""
        setattr(self, propname,propval)


    def map_dict_to_properties(self, dict):
        """Store dictionary 'dict' into the object's existing defined fields, and any fields that don't match, serialize into serialized_fields."""
        extrafields = {}
        fieldids = self.fieldhash.keys()
        # walk properties in dictionary and set object properties and extrafields dictionary
        for key in dict.keys():
            if (key in fieldids):
                # ok there is a field for this, so just save it
                self.set_property_byname(key, dict[key])
            else:
                # ok we don't have a field for it
                if (key not in self.ignored_logfields):
                    # add it to our extra fields dictionary to serialize
                    extrafields[key] = dict[key]
        # handle extrafields
        if (len(extrafields)==0):
            self.store_serialize_fields(None)
        else:
            self.store_serialize_fields(extrafields)







    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        # define fields list
        fieldlist = [
            # standard primary id number field
            mdbfield.DbfPrimaryId('id', {
                'label': "The primary key and id# for this row"
                }),
            # an arbitrarily long string serializing any other log properties that we don't have explicit fields for.
            mdbfield.DbfSerialized('serialized_fields', {
                'label': "The serialzed text version of the dictionary/array data being stored"
                }),
            # actual log msg text
            mdbfield.DbfTimestamp('timestamp', {
                'label': "The timestamp for the message"
                }),
            # actual log msg text
            mdbfield.DbfText('msg', {
                'label': "The text message"
                }),
            # actual log msg text
            mdbfield.DbfString('source', {
                'label': "The source of the message"
                }),
            # actual log msg text
            mdbfield.DbfString('type', {
                'label': "The type of the message"
                }),
            ]

        cls.hash_fieldlist(fieldlist)

