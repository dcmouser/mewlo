"""
settings.py
This file contains classes to support hierarchical settings.

We really don't do anything fancy here -- in fact some of it is a bit ugly and could use rewriting.

Essentially we are just maintaining a hierarchical dictionary with some support functions to ease access.

"""


# helper imports
from ..helpers.settings import settings
from dbmodel_settingsdict import DbModel_SettingsDictionary
import mewlo.mpackages.core.mglobals as mglobals
from ..helpers.misc import get_value_from_dict

# python imports
import datetime



class DbSettings(settings.Settings):
    """
    The DbSettings class provides a Settings-object interface to settings that are backed in a database.
    We have some desires for it:
        * For efficiency, we need to support the idea of loading and caching values in memory.
        * But because of distributed/multi-process applications, we may not be able to rely on using cached values.
        * But the machinery should be there in case we can use database-functionality to be informed about when db has changed and needs to be reloaded.
        * We want to support hierarchical serialized data containing multiple types, transparently.
    Other details:
        * Each DbSettings object is tied to a specific table (which it should be able to create dynamically).
    Strategy:
        * All requests will be handled by the normal code for using an in-memory dictionary to store and retrieve values.
        * We will keep the in-memory dictionary synchronized with a database table behind the scenes.
    """

    def __init__(self):
        # parent constructor
        super(DbSettings, self).__init__()
        # init
        self.dbmodelclass = None
        # keep track of date of last database sync
        self.sync_timestamps = {}
        self.sync_timestamp_all = None


    def startup(self, eventlist):
        """Any initial startup stuff to do?"""
        # parent constructor
        super(DbSettings, self).startup(eventlist)
        # ATTN: TO DO - set up database and open it
        # ATTN:TODO - FIX THIS to use a derived version of DbModel_SettingsDictionary with proper dbtablename
        self.dbmodelclass = mglobals.mewlosite().registry.get_class('DbModel_SettingsDictionary');
        #print "MODELCLASS: "+str(self.dbmodelclass)



    def shutdown(self):
        """Shutdown."""
        # pass



    def merge_settings(self, settingstoadd):
        """Just merge in a new dicitonary into our main dictionary."""
        self.db_lock()
        try:
            self.sync_load_properties(settingstoadd.keys())
            retv = super(DbSettings, self).merge_settings(settingstoadd)
            self.sync_save_properties(settingstoadd.keys())
        except Exception as exp:
            raise exp
        finally:
            self.db_unlock()
        return retv


    def merge_settings_property(self, propertyname, settingstoadd):
        """Merge in a new dicitonary into our main dictionary at a specific root section (creating root section if needed)."""
        self.db_lock()
        try:
            self.sync_load_properties([propertyname])
            retv = super(DbSettings, self).merge_settings_property(propertyname, settingstoadd)
            self.sync_save_properties([propertyname])
        except Exception as exp:
            raise
        finally:
            self.db_unlock()
        return retv


    def set_property(self, propertyname, value):
        """Set and overwrite a value at a section, replacing whatever was there."""
        retv = super(DbSettings, self).set_property(propertyname, value)
        self.sync_save_properties([propertyname])


    def get_value(self, propertyname, defaultval=None):
        """Lookup value from our settings dictionary and return it or default if not found."""
        self.sync_load_properties([propertyname])
        return super(DbSettings, self).get_value(propertyname, defaultval)


    def get_subvalue(self, propertyname, propertysubname, defaultval=None):
        """Lookup value from our settings dictionary at a certain root section, and return it or default if not found."""
        self.sync_load_properties([propertyname])
        return super(DbSettings, self).get_subvalue(propertyname, propertysubname, defaultval)



    def value_exists(self, propertyname, propertysubname=None):
        """Return true if the item existing in our settings dictionary (at specific root section if specified)."""
        self.sync_load_properties([propertyname])
        return super(DbSettings, self).value_exists(propertyname, propertysubname)


    def remove_all(self):
        """Clear contents of settings."""
        # clear all timestamps
        self.sync_timestamps = {}
        # and the setting saying all updated at this time
        safesynctime = self.get_synctime()
        update_sync_timestamp_all(safesynctime)
        # clear contents of the database
        self.db_remove_allproperties()
        # now hand off to parent class
        return super(DbSettings, self).remove_all()

    def remove_property(self, propertyname):
        """Clear contents of one property."""
        # clear timestamps for section
        del self.sync_timestamps[propertyname]
        # clear propertyname in the database
        self.db_remove_property(propertyname)
        # now hand off to parent class
        return super(DbSettings, self).remove_property(propertyname)



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        self.sync_load_all()
        return super(DbSettings, self).dumps(indent)


















    def sync_load_all(self):
        """Load entire settings (overwriting and removing now-empties)."""
        # if we're already sync'd, then nothing to do
        if (self.is_alreadysynced_all()):
            return
        # get synctime we will use below, BEFORE we access the database, to be conservative
        safesynctime = self.get_synctime()
        # clear current contents
        self.settingdict = {}
        self.sync_timestamps = {}
        # load ALL properties
        self.db_loadallproperties()
        # now update for each section to say we loaded it now
        for propertyname in self.settingdict:
            self.update_sync_timestamp(propertyname, safesynctime)
        # and the setting saying all updated at this time
        self.update_sync_timestamp_all(safesynctime)


    def sync_load_properties(self, propertynames):
        """Load one "section" into memory.
        We probably treat each section as a row, so this means a row. """
        # NOTE: Ideally we would have some way of knowing whether the in-memory dictionary is already sync'd with database without having to always reload.
        # on a coarse scale, we might do this by saving the date of the last read of the table, and not bothering to re-load if we know the table wasn't updated since then
        for propertyname in propertynames:
            if (not self.is_alreadysynced(propertyname)):
                # needs reloading
                # get synctime we will use below, BEFORE we access the database, to be conservative
                safesynctime = self.get_synctime()
                # load property
                self.db_loadproperty(propertyname)
                # now update last sync time
                self.update_sync_timestamp(propertyname, safesynctime)


    def sync_save_properties(self, propertynames):
        """Save one "section" to the database (overwriting whatever is there -- including removing values no longer references).
        We probably treat each section as a row, so this means a row."""
        for propertyname in propertynames:
            # get synctime we will use below, BEFORE we access the database, to be conservative
            safesynctime = self.get_synctime()
            # load property
            self.db_saveproperty(propertyname)
            # now update last sync time
            self.update_sync_timestamp(propertyname, safesynctime)



    def is_alreadysynced(self, propertyname):
        """Return True if we are confident that the database is unchanged since our last sync (i.e. if we know our in-memory dictionary is up to date)."""
        dbtimestamp = self.db_get_lastmodificationtime(propertyname)
        propertytimestamp = self.get_sync_timestamp(propertyname)
        if (dbtimestamp != None and propertytimestamp != None):
            # we have some times to compare
            if (dbtimestamp<=propertytimestamp):
                return True
        # no, or don't know
        return False

    def is_alreadysynced_all(self):
        """Return true if all properties are sync'd already."""
        dbtimestamp = self.db_get_lastmodificationtime_latest()
        if (dbtimestamp != None and self.sync_timestamp_all != None):
            # we have some times to compare
            if (dbtimestamp<=self.sync_timestamp_all):
                return True
        # no, or don't know
        return False



    def update_sync_timestamp(self, propertyname, synctime):
        """Update our internal record of when we last sync'd with database."""
        if (synctime==None):
            synctime = self.get_synctime()
        self.sync_timestamps[propertyname] = synctime

    def update_sync_timestamp_all(self, synctime):
        """Update our internal record of when we last sync'd with database."""
        if (synctime==None):
            synctime = self.get_synctime()
        self.sync_timestamp_all = synctime


    def get_sync_timestamp(self, propertyname):
        """Return datetime-compatible timestamp of when section was last loaded/saved, or None if we can't determine."""
        # note that it is impossible for timestamp_all to be more recent than an individual timestamp
        if (propertyname in self.sync_timestamps):
            return self.sync_timestamps[propertyname]
        # having no entry for this section, we can return timestamp_all rather than None, since any db changes before timestamp_all are already in memory
        return self.sync_timestamp_all


    def get_synctime(self):
        """We get the sync time before we do an operation, to be conservative."""
        return datetime.datetime.now()











    def db_lock(self):
        """Lock the db, while we read it, run a function, and then write out new values."""
        # ATTN: TODO
        pass

    def db_unlock(self):
        """Unlock the db after previous lock."""
        # ATTN: TODO
        pass

    def db_get_lastmodificationtime(self, propertyname):
        """Return datetime-compatible time of last database table modification, or None if we can't determine."""
        # Note that its fine to estimate this as long as we are conservative; that is if we aren't tracking modifcation date per section, we can return modification date of the whole table
        # ATTN:TODO - do per-property date estimage
        # For now, just return a conservative estimate: the last modification date of table as a whole
        return self.db_get_lastmodificationtime_latest()

    def db_get_lastmodificationtime_latest(self):
        """Return the most datetime-compatible time of most recent database table modification, or None if we can't determine."""
        # ATTN:TODO
        return None

    def db_remove_allproperties(self):
        """Remove all properties (rows) from the database table."""
        self.dbmodelclass.delete_all()

    def db_remove_property(self, propertyname):
        """Remove a specific property (row) from the database table."""
        self.dbmodelclass.delete_bykey({'keyname':propertyname})


    def db_loadproperty(self, propertyname):
        """Load a specific property (row) from the database table and unserialize it into self.settingdict[propertyname]."""
        # lookup row in database
        dictrow = self.dbmodelclass.find_one_bykey({'keyname':propertyname}, None)
        #print "DEBUGGING ONE db_loadproperty dictrow = "+str(dictrow)
        if (dictrow == None):
            propdict = {}
        else:
            propdict = dictrow.get_unserializeddict()
        # set it
        self.settingdict[propertyname] = propdict


    def db_saveproperty(self, propertyname):
        """Serialize and then save self.settingdict[propertyname] into the appropriate database row."""
        # create new model for setting row
        dictrow = self.dbmodelclass.new()
        dictrow.keyname = propertyname
        dictrow.storeserialize_dict(get_value_from_dict(self.settingdict, propertyname, None))
        #print "ATTN:DEBUG - IN db_saveproperty with keyname = {0} and serialized = {1}.".format(dictrow.keyname, dictrow.serializeddict)
        # save it
        dictrow.save()


    def db_loadallproperties(self):
        """Load all database rows and unserialize into self.settingdict."""
        # load all into memory
        dictrows = self.dbmodelclass.find_all()
        # clear current dictionary
        settingdict = {}
        # convert all
        for dictrow in dictrows:
            #print "DEBUGGING All ONE dictrow = "+str(dictrow)
            propertyname = dictrow.get_propertyname()
            self.settingdict[propertyname] = dictrow.get_unserializeddict()

