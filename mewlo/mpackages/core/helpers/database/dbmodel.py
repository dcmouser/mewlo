"""
dbmodel.py

This is our database object base class.

"""


# helper imports

# python imports
import pickle





class DbModel(object):
    """An object that represents a database model."""

    # class variables
    fields = []


    def __init__(self):
        """Constructor."""
        # init
        pass



    @classmethod
    def delete_all(cls):
        """Delete all items (rows) in the table."""
        # ATTN: TODO
        pass

    @classmethod
    def delete_bykey(cls,keydict):
        """Delete all items (rows) matching key dictionary settings."""
        # ATTN: TODO
        pass


    @classmethod
    def find_one_bykey(cls,keydict,defaultval):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        # ATTN: TODO
        return defaultval


    @classmethod
    def find_all(cls):
        """Load *all* rows and return them as array."""
        # ATTN: TODO
        return []


    @classmethod
    def serialize(cls, obj):
        """Serialize arbitrary object."""
        return pickle.dumps(obj)


    @classmethod
    def unserialize(cls, serializedtext):
        """Unserialize arbitrary text."""
        return pickle.loads(serializedtext)







    @classmethod
    def definedb(cls):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        pass


    @classmethod
    def register_fields(cls, fields):
        """The fields have been defined for the model."""
        # record fields
        self.fields = fields
        # register with database manager?
        # ATTN: TODO

