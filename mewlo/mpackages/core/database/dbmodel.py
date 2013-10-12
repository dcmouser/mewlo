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
    dbtablename = None
    dbschemaname = None
    #
    dbsqlatable = None
    dbsqlahelper = None
    dbmanager = None
    #
    fields = []


    def __init__(self):
        """Constructor."""
        # ATTN: NOTE THIS IS *NOT* CALLED WHEN INSTANTIATING MODELS VIA SQLALCHEMY ORM
        # init
        pass



    def dbm(self):
        """Shortcut to get info from class object."""
        return self.__class__.dbmanager


    def save(self):
        """Save the model to database."""
        self.dbm().model_save(self)







    @classmethod
    def store_dbdata(cls, sqlatable, sqlahelper, dbmanager):
        """Store data in class regarding datbase access for it."""
        # ATTN: TODO - some of this may not be needed, this may be automatically added to the class itself by sqlalchemy
        cls.dbsqlatable = sqlatable
        cls.dbsqlahelper = sqlahelper
        cls.dbmanager = dbmanager



    @classmethod
    def get_fields(cls):
        """Return the database fields."""
        return cls.fields


    @classmethod
    def delete_all(cls):
        """Delete all items (rows) in the table."""
        cls.dbmc().modelclass_deleteall(cls)


    @classmethod
    def delete_bykey(cls, keydict):
        """Delete all items (rows) matching key dictionary settings."""
        cls.dbmc().modelclass_deletebykey(cls, keydict)


    @classmethod
    def find_one_bykey(cls, keydict, defaultval):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        return cls.dbmc().modelclass_find_one_bykey(cls, keydict, defaultval)


    @classmethod
    def find_all(cls):
        """Load *all* rows and return them as array."""
        return cls.dbmc().modelclass_find_all(cls)


    @classmethod
    def serialize(cls, obj):
        """Serialize arbitrary object."""
        serializedtext = pickle.dumps(obj)
        #print "ATTN: the serialization of '{0}' is '{1}'.".format(str(obj),serializedtext)
        return serializedtext


    @classmethod
    def unserialize(cls, serializedtext):
        """Unserialize arbitrary text."""
        #print "ATTN: in unserialize asked to unserialized '{0}'.".format(serializedtext)
        return pickle.loads(str(serializedtext))

    @classmethod
    def new(cls):
        """Make a new instance of the class."""
        return cls()


    @classmethod
    def shutdown(cls):
        """Dummy code that needs to be cleaned up."""
        pass



    @classmethod
    def definedb(cls):
        """This class-level function defines the database fields for this model -- the columns, etc."""
        pass


    @classmethod
    def register_fields(cls, fields):
        """The fields have been defined for the model."""
        # record fields
        cls.fields = fields


    @classmethod
    def get_dbtablename(cls):
        return cls.dbtablename

    @classmethod
    def get_dbschemaname(cls):
        return cls.dbschemaname

    @classmethod
    def set_dbnames(cls, tablename, schemaname):
        cls.dbtablename = tablename
        cls.dbschemaname = schemaname

    @classmethod
    def dbmc(cls):
        return cls.dbmanager


