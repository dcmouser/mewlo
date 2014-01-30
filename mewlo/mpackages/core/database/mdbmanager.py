"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

# mewlo imports
from ..manager import manager



class MewloDatabaseManager(manager.MewloManager):
    """The MewloDatabaseManager supervises database support."""

    def __init__(self):
        super(MewloDatabaseManager,self).__init__()
        self.databasesettings = {}
        self.modelclasses = {}

    def startup(self, mewlosite, eventlist):
        super(MewloDatabaseManager,self).startup(mewlosite,eventlist)

    def shutdown(self):
        """
        Shutdown the database.
        Before we do, we flush it to save any pending saves.
        """
        super(MewloDatabaseManager,self).shutdown()
        self.commit_all_dbs()

        # model class resets to let go of sqla cached class vars
        self.reset_classdata_forallmodelclasses()





    def makedbtables(self):
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
        The one tricky thing is we may be called
        """
        # register it internally if its not already
        if (modelclass not in self.modelclasses):
            # store it
            self.modelclasses[modelclass.__name__] = modelclass
            # register it with the registry
            self.mewlosite.comp('registrymanager').register_class(owner, modelclass)

        # success
        return None


    def lookupclass(self, modelclassname):
        """Lookup a registered model class by name."""
        return self.modelclasses[modelclassname]




    def create_tableandmapper_forallmodelclasses(self):
        """We are ready to create all fields, THEN all relationships, for known model classes."""
        # It's important that we create all tabled before we try making ANY relationships, etc.
        self.create_prerequisites_forallmodelclasses()
        self.create_table_forallmodelclasses()
        self.create_mapper_forallmodelclasses()
        # now ask db engine to actually BUILD all tables for all models
        self.makedbtables()
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
            modelclass.create_table(self)
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




    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "DatabaseManager (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += " "*indent + " Settings: "+str(self.databasesettings)
        return outstr

