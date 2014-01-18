"""
mdbmodel.py

This is our database object base class.

"""


# mewlo imports
from ..helpers import misc
import mdbfield

# python imports
import pickle

# library imports
import sqlalchemy
import sqlalchemy.orm






class MewloDbModel(object):
    """An object that represents a database model."""

    # class variables
    dbtablename = None
    dbschemaname = None

    # ATTN: 1/16/14 - see reset_classdata(cls), which duplicates some of this
    #
    dbsqlatable = None
    dbsqlahelper = None
    dbmanager = None
    #
    did_create_table = False
    did_create_mapper = False
    did_create_prerequisites = False
    isreadytodb = False
    #
    fieldlist = []
    fieldhash = {}




    @classmethod
    def reset_classdata(cls):
        """
        Reset calculcated class variables.
        This is kludgey and confusing.
        We use these class variables to track some sqlalchemy stuff, but when performing unit tests we need this to reset before each test.
        """
        #
        cls.dbsqlatable = None
        cls.dbsqlahelper = None
        cls.dbmanager = None
        #
        cls.did_create_table = False
        cls.did_create_mapper = False
        cls.did_create_prerequisites = False
        cls.isreadytodb = False
        #
        cls.fieldlist = []
        cls.fieldhash = {}










    def gobify(self):
        """Create a gob global unique resource object for us.  The gob table stores the type of object it refers to (but not the foreign id in order to stay normalized)."""
        import mdbmodel_gob
        self.gob = mdbmodel_gob.MewloDbModel_Gob()
        objtypename = self.calc_gobtypename()
        self.gob.objecttype = objtypename
        return self.gob

    def calc_gobtypename(self):
        return self.get_dbtablename()






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
    def get_dbsqlatable(cls):
        return cls.dbsqlatable

    @classmethod
    def override_dbnames(cls, tablename, schemaname):
        cls.dbtablename = tablename
        cls.dbschemaname = schemaname



    @classmethod
    def extend_fields(cls, addfieldlist, flag_front=False):
        """Add fields."""
        # we need to do a kludgey thing here because derived classes inherit default value from parent, and extending that list would be bad.
        if (len(cls.fieldlist)==0 or cls.fieldlist == MewloDbModel.fieldlist):
            cls.fieldlist=addfieldlist
        else:
            if (flag_front):
                cls.fieldlist = addfieldlist + cls.fieldlist
            else:
                cls.fieldlist.extend(addfieldlist)


    @classmethod
    def get_fieldlist(cls):
        """Return the database fields."""
        return cls.fieldlist

    @classmethod
    def hash_fieldlist(cls):
        """hash fieldlist in dictionary."""
        for field in cls.fieldlist:
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
    def get_isreadytodb(cls):
        """Return True if this class is ready to access the database (fields have been created, etc.)."""
        return cls.isreadytodb

    @classmethod
    def set_isreadytodb(cls, val):
        """Return True if this class is ready to access the database (fields have been created, etc.)."""
        cls.isreadytodb = val























    @classmethod
    def create_prerequisites(cls, dbmanager):
        """Create and register with the dbmanager any prerequisites that this class uses."""
        # nothing to do in base class
        pass




    @classmethod
    def create_table(cls, dbmanager):
        """Default way of creating sql alchemy columns for model."""

        # ask model to define its internal fields
        fields = cls.define_fields(dbmanager)
        cls.extend_fields(fields, True)
        # now hash the fieldlist so we can look up fields by name
        cls.hash_fieldlist()

        # get the sqlahelper for this schema (usually default one shared by all models), plus some info
        dbtablename = cls.get_dbtablename()
        dbschemaname = cls.get_dbschemaname()
        sqlahelper = dbmanager.get_sqlahelper(dbschemaname)
        metadata = sqlahelper.getmake_metadata()

        # build sqlalchemy columns from fields
        sqlalchemycolumns = cls.create_sqlalchemy_columns_from_dbfields()

        # tell sqlalchemy to build table object from columns
        modeltable = sqlalchemy.Table(dbtablename, metadata, *sqlalchemycolumns)

        # and store the table and other object references in the model class itself
        cls.setclass_dbinfo(modeltable, sqlahelper, dbmanager)




    @classmethod
    def create_mapper(cls, dbmanager):
        """Default way of creating sql alchemy mapper and relations for model."""

        # get previously built modeltable
        modeltable = cls.get_dbsqlatable()

        # build sqlalchemy mapper properties from fields
        mapproperties = cls.create_sqlalchemy_mapperproperties_from_dbfields(modeltable)

        # tell sqlalchemy to build mapper
        sqlalchemy.orm.mapper(cls, modeltable, properties=mapproperties)







    @classmethod
    def create_sqlalchemy_columns_from_dbfields(cls):
        """
        Given a list of our internal fields, build sqlalchemy columns.
        """
        allcolumns = []
        for field in cls.fieldlist:
            columns = field.create_sqlalchemy_columns(cls)
            # IMPORTANT - we need to save the sqla columns associated with a field, so that callers can look them up if they need to later
            # this is done for example when creating relations between tables when we need to specify foreign_keys parameter
            field.set_sqlacolumns(columns)
            if (columns!=None):
                allcolumns.extend(columns)
        return allcolumns


    @classmethod
    def create_sqlalchemy_mapperproperties_from_dbfields(cls,modeltable):
        """
        Given a list of our internal fields, build sqlalchemy mapper properties.
        """
        allprops = {}
        #
        for field in cls.fieldlist:
            props = field.create_sqlalchemy_mapperproperties(cls,modeltable)
            if (props!=None):
                allprops.update(props)
        return allprops




    @classmethod
    def lookup_sqlacolumnlist_for_field(cls, fieldid):
        """Try to find the list of sqlacolumns associated with a field."""
        for field in cls.fieldlist:
            if (field.id==fieldid):
                return field.get_sqlacolumns()
        return None



    @classmethod
    def lookup_sqlacolumn_for_field(cls, fieldid):
        """Try to find the list of sqlacolumns associated with a field."""
        for field in cls.fieldlist:
            if (field.id==fieldid):
                return field.get_sqlacolumn()
        raise Exception("Could not find field {0}".format(fieldid))
        #return None

















    # These methods will be specific to the derived subclass

    @classmethod
    def define_fields(cls, dbmanager):
        """
        This class-level function defines the database fields for this model -- the columns, etc.
        The subclass will implement this function.
        Return a list of dbfields.
        """
        return []







