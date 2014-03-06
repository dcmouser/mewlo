"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

# mewlo imports
from ..manager import manager

# for core model creation
from ..user import muser
from ..group import mgroup
from ..rbac import mrbac
from ..session import msession
from ..verification import mverification
import mdbsettings, mdbmanager_sqlalchemy, mdbmodel_settings, mdbmodel_gob
from ..setting.msettings import MewloSettings






class MewloDatabaseManager(manager.MewloManager):
    """The MewloDatabaseManager supervises database support."""

    # class constants
    description = "Databae manager provides the API interface for database operations"
    typestr = "core"


    def __init__(self, mewlosite, debugmode):
        super(MewloDatabaseManager,self).__init__(mewlosite, debugmode)
        self.databasesettings = {}
        self.modelclasses = {}


    def prestartup_register(self, eventlist):
        """Register core database models."""
        # call parent
        super(MewloDatabaseManager,self).prestartup_register(eventlist)
        # register the gob (global object) model; all users/groups/etc have a unique gob id; it lets us set up foreign keys to dif kinds of objects via their gob id
        self.register_modelclass(self, mdbmodel_gob.MewloDbModel_Gob)
        # user group role stuff
        self.register_modelclass(self, muser.MewloUser)
        self.register_modelclass(self, mgroup.MewloGroup)
        self.register_modelclass(self, mrbac.MewloRole)
        self.register_modelclass(self, mrbac.MewloRoleEntails)
        self.register_modelclass(self, mrbac.MewloRoleAssignment)
        # session
        self.register_modelclass(self, msession.MewloSession)
        # verification
        self.register_modelclass(self, mverification.MewloVerification)


    def startup(self, eventlist):
        super(MewloDatabaseManager,self).startup(eventlist)


    def shutdown(self):
        """
        Shutdown the database.
        Before we do, we flush it to save any pending saves.
        """
        super(MewloDatabaseManager,self).shutdown()
        self.commit_all_dbs()

        # model class resets to let go of sqla cached class vars
        self.reset_classdata_forallmodelclasses()





    def makedbtables_all(self):
        """Implemented by subclass to create all database tables from registered models."""
        pass

    def makedbtable_one(self, tablename):
        """Implemented by subclass to create all database tables from registered models."""
        pass



    def set_databasesettings(self, databasesettings):
        """Simple accessor."""
        self.databasesettings = databasesettings
        #print "ATTN: DATABASE SETTINGS1 ARE: "+str(self.databasesettings)

















    def process_request_ends(self, request):
        """Do stuff before processing a request."""
        self.commitdb_on_request_ends()

    def commit_on_request_ends(self):
        """Nothing to do in base class."""
        pass

    def commit_all_dbs(self):
        """Nothing to do in base class."""
        pass















    def resolve(self, text):
        """Sometimes database engine configuration settings will use mewlo aliases like {$databasedirectory}, etc.  This resolves them."""
        return self.mewlosite.resolve(text)














    def create_derived_dbmodelclass(self, owner, baseclass, classname=None, tablename=None, schemaname='default'):
        """
        Create a new *CLASS* based on another model class, with a custom classname and tablename.
        We only need to use this when we want to dynamically create multiple tables based from the same base model class.
        NOTE: This function does *not* register the class with Mewlo and define its database fields.
        """
        # create the new class
        if (classname==None):
            targetclass = baseclass
        else:
            #print "Creating class {0} from class {1}.".format(classname,baseclass.__name__)
            targetclass = type(classname, (baseclass,),{})
        # tablename
        if (tablename==None):
            tablename=targetclass.__name__
        # set table info
        targetclass.override_dbnames(tablename, schemaname)
        # and return it
        return targetclass










    def register_modelclass(self, owner, modelclass):
        """Register a datbase model class.
        Note that in doing this, we do not yet create columns and fields for it, we are simply telling the database manager it exists.
        It is essential that EVERY model class used in any fashion register itself in this way, so that the tables get created and the manager get set for the modelclass
        Which also lets model classes know about any tablename prefixes, etc.
        """
        # register it internally if its not already
        if (modelclass not in self.modelclasses):
            # store it
            self.modelclasses[modelclass.__name__] = modelclass
            # register it with the registry
            #print "ATTN: IN register_modelclass with mewlosite = {0}.".format(str(self.mewlosite))
            self.mewlosite.comp('registrymanager').register_class(owner, modelclass)
            # and now call into the modelclass to tell them about the manager that owns them (this is used by the model class when creating tables, etc.)
            modelclass.set_dbm(self)

        # success
        return None


    def lookupclass(self, modelclassname):
        """Lookup a registered model class by name."""
        return self.modelclasses[modelclassname]




    def create_tableandmapper_foroneclass(self, modelclass):
        """We are ready to create all fields, THEN all relationships, for a specific model classes."""
        # It's important that we create all tabled before we try making ANY relationships, etc.
        self.create_prerequisites_formodelclass(modelclass)
        self.create_table_formodelclass(modelclass)
        self.create_mapper_formodelclass(modelclass)
        # now ask db engine to actually BUILD all tables for all models
        self.makedbtable_one(modelclass.get_dbtablename())
        # mark models as ready to be used
        self.set_isreadytodb_formodelclass(modelclass)



    def create_tableandmapper_forallmodelclasses(self):
        """We are ready to create all fields, THEN all relationships, for known model classes."""
        # It's important that we create all tabled before we try making ANY relationships, etc.
        self.create_prerequisites_forallmodelclasses()
        self.create_table_forallmodelclasses()
        self.create_mapper_forallmodelclasses()
        # now ask db engine to actually BUILD all tables for all models
        self.makedbtables_all()
        # mark models as ready to be used
        self.set_isreadytodb_forallmodelclasses()




    def create_prerequisites_forallmodelclasses(self):
        """Create fields for all registered model classes (that haven't already been created)."""
        # ATTN: TODO - This is somewhat odd and needs to be looked into, because we can end up adding modelclasses within these calls to create_prereqs; it's not clear we handle that case properly
        # in other words recursive prerequisitite class creation may fail
        modeclasskeys = self.modelclasses.keys()
        for key in modeclasskeys:
            # map database fields for it
            modelclass = self.modelclasses[key]
            self.create_prerequisites_formodelclass(modelclass)

    def create_table_forallmodelclasses(self):
        """Create fields for all registered model classes (that haven't already been created)."""
        for key,val in self.modelclasses.iteritems():
            # map database fields for it
            self.create_table_formodelclass(val)

    def create_mapper_forallmodelclasses(self):
        """Create relationships for all registered model classes (that haven't already been created)."""
        for key,val in self.modelclasses.iteritems():
            # map database fields for it
            self.create_mapper_formodelclass(val)

    def set_isreadytodb_forallmodelclasses(self):
        """Set ready flag for all model classes."""
        for key,val in self.modelclasses.iteritems():
            # map database fields for it
            self.set_isreadytodb_formodelclass(val)

    def reset_classdata_forallmodelclasses(self):
        """Reset all chached data for sqla database stuff for model classes."""
        for key,val in self.modelclasses.iteritems():
            # map database fields for it
            self.reset_classdata_forallmodelclasse(val)





    def create_prerequisites_formodelclass(self, modelclass):
        """Create the fields for this model."""
        if (isinstance(modelclass,basestring)):
            modelclass = self.modelclasses[modelclass]
        if (not modelclass.did_create_prerequisites):
            # ask model to create and register any prerequisites (helper classes, etc.)
            modelclass.create_prerequisites(self)
            # set flag saying its been done
            modelclass.did_create_prerequisites = True

    def create_table_formodelclass(self, modelclass):
        """Create the fields for this model."""
        if (isinstance(modelclass,basestring)):
            modelclass = self.modelclasses[modelclass]
        if (not modelclass.did_create_table):
            # create the fields
            modelclass.create_table()
            # set flag saying its been done
            modelclass.did_create_table = True

    def create_mapper_formodelclass(self, modelclass):
        """Create the relationships for this model."""
        if (isinstance(modelclass,basestring)):
            modelclass = self.modelclasses[modelclass]
        if (not modelclass.did_create_mapper):
            modelclass.create_mapper(self)
            # set flag saying its been done
            modelclass.did_create_mapper = True

    def set_isreadytodb_formodelclass(self, modelclass):
        """Set ready flag for this model."""
        if (isinstance(modelclass,basestring)):
            modelclass = self.modelclasses[modelclass]
        modelclass.set_isreadytodb(True)

    def reset_classdata_forallmodelclasse(self, modelclass):
        """Reset cached sqla database data."""
        if (isinstance(modelclass,basestring)):
            modelclass = self.modelclasses[modelclass]
        modelclass.reset_classdata()












    def get_tablenameprefix(self, schemaname):
        """
        Return the prefix that should be used on a table in the specified schema.
        In common use this will be an empty string.
        """
        return self.get_schemasettings_val(schemaname,'tablename_prefix','')





    def get_schemasettings_val(self, schemaname, keyname, defaultval):
        """Lookup a setting value for a schema, falling back to default schema; if still not found return default."""
        # if already in our collection, just return it
        if (schemaname in self.databasesettings):
            schemasettings = self.databasesettings[schemaname]
            if (keyname in schemasettings):
                return schemasettings[keyname]
        # not there, so look for a default schema
        schemaname = 'default'
        if (schemaname in self.databasesettings):
            schemasettings = self.databasesettings[schemaname]
            if (keyname in schemasettings):
                return schemasettings[keyname]
        # not found, use default
        return defaultval









    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "DatabaseManager (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += self.dumps_description(indent+1)
        outstr += " "*indent + " Settings: "+str(self.databasesettings)+"\n"
        return outstr

