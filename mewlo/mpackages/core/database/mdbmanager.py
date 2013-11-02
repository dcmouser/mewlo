"""
mdbmanager.py
This module contains Mewlo database manager class.
"""

# mewlo imports




class MewloDatabaseManager(object):
    """The MewloDatabaseManager supervises database support."""

    def __init__(self):
        self.databasesettings = {}
        self.modelclasses = {}

    def startup(self, mewlosite, eventlist):
        self.mewlosite = mewlosite

    def shutdown(self):
        """Shutdwn the database.
        Before we do, we flush it to save any pending saves."""
        self.flush_all_dbs()





    def makedbtables(self):
        pass


    def set_databasesettings(self, databasesettings):
        """Simple accessor."""
        self.databasesettings = databasesettings
        #print "ATTN: DATABASE SETTINGS1 ARE: "+str(self.databasesettings)

















    def process_request_starts(self, request):
        """Do stuff before processing a request."""
        pass

    def process_request_ends(self, request):
        """Do stuff before processing a request."""
        self.flushdb_on_request_ends()

    def flushdb_on_request_ends(self):
        """Nothing to do in base class."""
        pass

    def flush_all_dbs(self):
        """Nothing to do in base class."""
        pass















    def resolve(self, text):
        """Sometimes database engine configuration settings will use mewlo aliases like {$databasedirectory}, etc.  This resolves them."""
        return self.mewlosite.resolve(text)














    def create_derived_dbmodelclass(self, owner, baseclass, classname=None, tablename=None, schemaname='default'):
        """
        Create a new *CLASS* based on another model class, with a custom classname and tablename.
        We only need to use this when we want to dynamically create multiple tables based from the same base model class.
        NOTE: This function does *not* register the class and define its database fields.
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
        # register it internally
        # ask model to create and register any helper classes
        modelclass.create_helper_modelclasses(self)
        # now add it to registry if its not already
        if (modelclass not in self.modelclasses):
            self.modelclasses[modelclass.__name__] = modelclass
            # register it with the registry
            self.mewlosite.registry.register_class(owner, modelclass)
        # success
        return None




    def create_tableandmapper_forallmodelclasses(self):
        """We are ready to create all fields, THEN all relationships, for known model classes."""
        # ATTN: because create_table is creating new models, we need to call this multiple times; fix this!
        self.create_table_forallmodelclasses()
        self.create_mapper_forallmodelclasses()
        # now ask db engine to actually BUILD all tables for all models
        self.makedbtables()




    def create_table_forallmodelclasses(self):
        """Create fields for all registered model classes (that haven't already been created)."""
        for key in self.modelclasses.keys():
            # map database fields for it
            modelclass = self.modelclasses[key]
            self.create_table_formodelclass(modelclass)


    def create_mapper_forallmodelclasses(self):
        """Create relationships for all registered model classes (that haven't already been created)."""
        for key in self.modelclasses.keys():
            # map database fields for it
            modelclass = self.modelclasses[key]
            self.create_mapper_formodelclass(modelclass)



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










    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "DatabaseManager (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += " "*indent + " Settings: "+str(self.databasesettings)
        return outstr
