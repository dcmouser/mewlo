"""
mdbmodel.py

This is our database object base class.

"""


# mewlo imports
from ..helpers import misc
import mdbfield

# python imports
import pickle






class MewloDbModel(object):
    """An object that represents a database model."""

    # class variables
    dbtablename = None
    dbschemaname = None
    #
    dbsqlatable = None
    dbsqlahelper = None
    dbmanager = None
    #
    did_register_fields = False
    did_register_relations = False
    #
    fieldlist = []
    fieldhash = {}



    # ATTN: NOTE __INIT__ IS *NOT* CALLED WHEN INSTANTIATING MODELS VIA SQLALCHEMY ORM SO WE AVOID IT WHERE POSSIBLE


















    # These methods should not have to be re-implemented by dervived subclasses

    def add(self):
        """Add the model to database."""
        self.dbm().model_add(self)

    def save(self):
        """Update/Save the model to database."""
        self.add()

    def delete(self):
        """Delete the model from database."""
        self.dbm().model_delete(self)





    @classmethod
    def dbm(cls):
        """Shortcut to get info from class object."""
        return cls.dbmanager

    @classmethod
    def dbsession(cls):
        """Shortcut to get info from class object."""
        sqlahelper = cls.dbsqlahelper
        return sqlahelper.getmake_session()

    @classmethod
    def get_dbtablename(cls):
        return cls.dbtablename

    @classmethod
    def get_dbschemaname(cls):
        return cls.dbschemaname

    @classmethod
    def setclass_dbinfo(cls, sqlatable, sqlahelper, dbmanager):
        """Store data in class regarding datbase access for it."""
        # ATTN: TODO - some of this may not be needed, this may be automatically added to the class itself by sqlalchemy
        cls.dbsqlatable = sqlatable
        cls.dbsqlahelper = sqlahelper
        cls.dbmanager = dbmanager

    @classmethod
    def override_dbnames(cls, tablename, schemaname):
        cls.dbtablename = tablename
        cls.dbschemaname = schemaname

    @classmethod
    def get_fieldlist(cls):
        """Return the database fields."""
        return cls.fieldlist

    @classmethod
    def get_dbsqlatable(cls):
        return cls.dbsqlatable

    @classmethod
    def hash_fieldlist(cls, fieldlist):
        """hash fieldlist in dictionary."""
        cls.fieldlist = fieldlist
        for field in fieldlist:
            cls.fieldhash[field.id] = field




    @classmethod
    def delete_all(cls):
        """Delete all items (rows) in the table."""
        cls.dbm().modelclass_deleteall(cls)

    @classmethod
    def delete_bykey(cls, keydict):
        """Delete all items (rows) matching key dictionary settings."""
        cls.dbm().modelclass_deletebykey(cls, keydict)

    @classmethod
    def find_one_bykey(cls, keydict, defaultval):
        """Find and return an instance object for the single row specified by keydict.
        :return: defaultval if not found
        """
        return cls.dbm().modelclass_find_one_bykey(cls, keydict, defaultval)

    @classmethod
    def find_all(cls):
        """Load *all* rows and return them as array."""
        return cls.dbm().modelclass_find_all(cls)

    @classmethod
    def serialize(cls, obj):
        """Helper function to serialize arbitrary object."""
        return misc.serialize_for_readability(obj)

    @classmethod
    def unserialize(cls, serializedtext):
        """Helper function to unserialize arbitrary text."""
        return pickle.loads(str(serializedtext))

    @classmethod
    def new(cls):
        """Make a new instance of the class."""
        return cls()


    @classmethod
    def get_readytodb(cls):
        """Return True if this class is ready to access the database (fields have been created, etc.)."""
        return cls.did_register_fields




    @classmethod
    def create_helper_modelclasses(cls, dbmanager):
        """Create and register with the dbmanager any model classes that this class uses as helpers."""
        pass


    @classmethod
    def create_fields(cls, dbmanager):
        #print "TESTDEBUG: create_fields for "+cls.__name__
        if (cls.did_register_fields):
            return
        cls.did_register_fields = True
        dbmanager.create_fields_onbehalfof_model(cls)


    @classmethod
    def create_relations(cls, dbmanager):
        if (cls.did_register_relations):
            return
        cls.did_register_relations = True
        dbmanager.create_relations_onbehalfof_model(cls)











    # These methods will be specific to the derived subclass

    @classmethod
    def definedb(cls, dbmanager):
        """This class-level function defines the database fields for this model -- the columns, etc.
        The subclass will implement this function."""
        pass







