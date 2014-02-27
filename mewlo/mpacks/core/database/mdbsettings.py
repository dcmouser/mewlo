"""
mdbsettings.py
This file contains classes to support hierarchical settings.
We really don't do anything fancy here -- in fact some of it is a bit ugly and could use rewriting.
Essentially we are just maintaining a hierarchical dictionary with some support functions to ease access.

ATTN: this code has become a bit kludgey and could use some rewriting.
"""


# helper imports
from ..setting.msettings import MewloSettings
from ..helpers.misc import get_value_from_dict
from ..database import mdbmodel_settings

# python imports
import datetime



class MewloSettingsDb(MewloSettings):
    """
    The MewloSettingsDb class provides a Settings-object interface to settings that are backed in a database.
    We have some desires for it:
        * For efficiency, we need to support the idea of loading and caching values in memory.
        * But because of distributed/multi-process applications, we may not be able to rely on using cached values.
        * But the machinery should be there in case we can use database-functionality to be informed about when db has changed and needs to be reloaded.
        * We want to support hierarchical serialized data containing multiple types, transparently.
    Other details:
        * Each MewloSettingsDb object is tied to a specific table via a db model class (which it can construct dynamically).
    Strategy:
        * All requests will be handled by the normal code for using an in-memory dictionary to store and retrieve values.
        * We will keep the in-memory dictionary synchronized with a database table behind the scenes.
        * We must allow that other processes may be trying to modify the data at the same time as us, so we only trust our cached values IFF the database supports a way of telling when a row was last written
        * Furthermore, some operations require a read and then write of a row, and we would like to lock the table/row during such operations.
    """

    # class var
    dbmodelclass = None


    def __init__(self, mewlosite, debugmode):
        # parent constructor
        super(MewloSettingsDb, self).__init__(mewlosite, debugmode)
        # keep track of date of last database sync
        self.sync_timestamps = {}
        self.sync_timestamp_all = None


    def prestartup_register(self, eventlist):
        """
        Called before starting up, to ask managers to register any database classes BEFORE they may be used in startup.
        In this case we create a new db model class dynamically, right now, based on parameters passed to us at time of initialization.
        This makes it particularly easy for us to create new database-settings tables.
        ATTN: As neat as this is, I think it would be better to not do this, and to require a separate thin derived class for each settings table.
        """
        # call parent
        super(MewloSettingsDb,self).prestartup_register(eventlist)
        # build and set self.dbmodelclass
        self.buildset_dbmodelclass()
        # register model class
        self.mewlosite.comp('dbmanager').register_modelclass(self, self.dbmodelclass)


    def buildset_dbmodelclass(self):
        """Can be overridden by derived classes, by default uses class var."""
        self.dbmodelclass = self.__class__.dbmodelclass


    def startup(self, eventlist):
        """Any initial startup stuff to do?"""
        # parent constructor
        super(MewloSettingsDb, self).startup(eventlist)


    def shutdown(self):
        """Shutdown."""
        # parent
        super(MewloSettingsDb, self).shutdown()



    def merge_settings(self, settingstoadd):
        """Just merge in a new dictionary into our main dictionary."""
        self.db_lock(settingstoadd.keys())
        try:
            self.sync_load_keys(settingstoadd.keys())
            retv = super(MewloSettingsDb, self).merge_settings(settingstoadd)
            self.sync_save_keys(settingstoadd.keys())
        except Exception as exp:
            raise exp
        finally:
            self.db_unlock()
        return retv


    def merge_settings_key(self, keyname, settingstoadd):
        """Merge in a new dictionary into our main dictionary at a specific root section (creating root section if needed)."""
        self.db_lock(settingstoadd.keys())
        try:
            self.sync_load_keys([keyname])
            retv = super(MewloSettingsDb, self).merge_settings_key(keyname, settingstoadd)
            self.sync_save_keys([keyname])
        except Exception as exp:
            raise
        finally:
            self.db_unlock()
        return retv


    def merge_settings_subkey(self, keyname, subkeyname, settingstoadd):
        """Merge in a new dicitonary into our main dictionary at a specific root section (creating root section if needed)."""
        self.db_lock(settingstoadd.keys())
        try:
            self.sync_load_keys([keyname])
            retv = super(MewloSettingsDb, self).merge_settings_subkey(keyname, keysubname, settingstoadd)
            self.sync_save_keys([keyname])
        except Exception as exp:
            raise
        finally:
            self.db_unlock()
        return retv



    def set(self, newsettings):
        """Set and overwrite a value at a section, replacing whatever was there."""
        self.db_lock([])
        try:
            self.remove_all()
            retv = super(MewloSettingsDb, self).set(newsettings)
            self.sync_save_keys(newsettings.keys())
        except Exception as exp:
            raise
        finally:
            self.db_unlock()
        return retv


    def update(self, newsettings):
        """Update and overwrite a value at a section, replacing whatever was there."""
        self.db_lock([])
        try:
            retv = super(MewloSettingsDb, self).update(newsettings)
            self.sync_save_keys(newsettings.keys())
        except Exception as exp:
            raise
        finally:
            self.db_unlock()
        return retv


    def get(self):
        """Get all."""
        self.sync_load_all()
        return super(MewloSettingsDb, self).get()


    def set_key(self, keyname, value):
        """Set and overwrite a value at a section, replacing whatever was there."""
        retv = super(MewloSettingsDb, self).set_key(keyname, value)
        self.sync_save_keys([keyname])


    def get_value(self, keyname, defaultval=None):
        """Lookup value from our settings dictionary and return it or default if not found."""
        self.sync_load_keys([keyname])
        return super(MewloSettingsDb, self).get_value(keyname, defaultval)


    def get_subvalue(self, keyname, keysubname, defaultval=None):
        """Lookup value from our settings dictionary at a certain root section, and return it or default if not found."""
        self.sync_load_keys([keyname])
        return super(MewloSettingsDb, self).get_subvalue(keyname, keysubname, defaultval)


    def get_subsubvalue(self, keyname, keysubname, keysubsubname, defaultval=None):
        """Lookup value from our settings dictionary at a certain root section, and return it or default if not found."""
        self.sync_load_keys([keyname])
        return super(MewloSettingsDb, self).get_subsubvalue(keyname, keysubname, keysubsubname, defaultval)



    def value_exists(self, keyname, keysubname=None):
        """Return true if the item existing in our settings dictionary (at specific root section if specified)."""
        self.sync_load_keys([keyname])
        return super(MewloSettingsDb, self).value_exists(keyname, keysubname)


    def remove_all(self):
        """Clear contents of settings."""
        # clear all timestamps
        self.sync_timestamps = {}
        # and the setting saying all updated at this time
        safesynctime = self.get_synctime()
        update_sync_timestamp_all(safesynctime)
        # clear contents of the database
        self.db_remove_allkeys()
        # now hand off to parent class
        return super(MewloSettingsDb, self).remove_all()


    def remove_key(self, keyname):
        """Clear contents of one key."""
        # we are just removing an entire row
        # clear timestamps for section
        del self.sync_timestamps[keyname]
        # clear keyname in the database
        self.db_remove_key(keyname)
        # now hand off to parent class
        return super(MewloSettingsDb, self).remove_key(keyname, keysubname)


    def remove_subkey(self, keyname, keysubname):
        """Clear contents of one subkey."""
        # this is basically a load, followed by a modification, then a save; almost identical to a set_subvalue or merge
        self.db_lock([keyname])
        try:
            # load to get most recent values
            self.sync_load_keys([keyname])
            # now hand off to parent class
            retv = super(MewloSettingsDb, self).remove_subkey(keyname, keysubname)
            # now save
            self.sync_save_keys([keyname])
        except Exception as exp:
            raise exp
        finally:
            self.db_unlock()
        return retv




    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        self.sync_load_all()
        return super(MewloSettingsDb, self).dumps(indent)


















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
        # load ALL keys
        self.db_loadallkeys()
        # now update for each section to say we loaded it now
        for keyname in self.settingdict:
            self.update_sync_timestamp(keyname, safesynctime)
        # and the setting saying all updated at this time
        self.update_sync_timestamp_all(safesynctime)


    def sync_load_keys(self, keynames):
        """Load one or more sections (row) into memory."""
        # NOTE: Ideally we would have some way of knowing whether the in-memory dictionary is already sync'd with database without having to always reload.
        # on a coarse scale, we might do this by saving the date of the last read of the table, and not bothering to re-load if we know the table wasn't updated since then
        for keyname in keynames:
            if (not self.is_alreadysynced(keyname)):
                # needs reloading
                # get synctime we will use below, BEFORE we access the database, to be conservative
                safesynctime = self.get_synctime()
                # load key
                self.db_loadkey(keyname)
                # now update last sync time
                self.update_sync_timestamp(keyname, safesynctime)


    def sync_save_keys(self, keynames):
        """Save one "section" to the database (overwriting whatever is there -- including removing values no longer references).
        We probably treat each section as a row, so this means a row."""
        for keyname in keynames:
            # get synctime we will use below, BEFORE we access the database, to be conservative
            safesynctime = self.get_synctime()
            # load key
            self.db_savekey(keyname)
            # now update last sync time
            self.update_sync_timestamp(keyname, safesynctime)











    def is_alreadysynced(self, keyname):
        """Return True if we are confident that the database is unchanged since our last sync (i.e. if we know our in-memory dictionary is up to date)."""
        dbtimestamp = self.db_get_lastmodificationtime(keyname)
        keytimestamp = self.get_sync_timestamp(keyname)
        if (dbtimestamp != None and keytimestamp != None):
            # we have some times to compare
            if (dbtimestamp<=keytimestamp):
                return True
        # no, or don't know
        return False

    def is_alreadysynced_all(self):
        """Return true if all keys are sync'd already."""
        dbtimestamp = self.db_get_lastmodificationtime_latest()
        if (dbtimestamp != None and self.sync_timestamp_all != None):
            # we have some times to compare
            if (dbtimestamp<=self.sync_timestamp_all):
                return True
        # no, or don't know
        return False



    def update_sync_timestamp(self, keyname, synctime):
        """Update our internal record of when we last sync'd with database."""
        if (synctime==None):
            synctime = self.get_synctime()
        self.sync_timestamps[keyname] = synctime

    def update_sync_timestamp_all(self, synctime):
        """Update our internal record of when we last sync'd with database."""
        if (synctime==None):
            synctime = self.get_synctime()
        self.sync_timestamp_all = synctime


    def get_sync_timestamp(self, keyname):
        """Return datetime-compatible timestamp of when section was last loaded/saved, or None if we can't determine."""
        # note that it is impossible for timestamp_all to be more recent than an individual timestamp
        if (keyname in self.sync_timestamps):
            return self.sync_timestamps[keyname]
        # having no entry for this section, we can return timestamp_all rather than None, since any db changes before timestamp_all are already in memory
        return self.sync_timestamp_all


    def get_synctime(self):
        """We get the sync time before we do an operation, to be conservative."""
        return datetime.datetime.now()
















    def db_lock(self, keynames):
        """Lock the db, while we read it, run a function, and then write out new values."""
        # ATTN: TODO
        pass


    def db_unlock(self):
        """Unlock the db after previous lock."""
        # ATTN: TODO
        pass


    def db_get_lastmodificationtime(self, keyname):
        """Return datetime-compatible time of last database table modification, or None if we can't determine."""
        # Note that its fine to estimate this as long as we are conservative; that is if we aren't tracking modifcation date per section, we can return modification date of the whole table
        # ATTN:TODO - do per-key date estimage
        # For now, just return a conservative estimate: the last modification date of table as a whole
        return self.db_get_lastmodificationtime_latest()


    def db_get_lastmodificationtime_latest(self):
        """Return the most datetime-compatible time of most recent database table modification, or None if we can't determine."""
        # ATTN:TODO
        return None


    def db_remove_allkeys(self):
        """Remove all keys (rows) from the database table."""
        self.dbmodelclass.delete_all()


    def db_remove_key(self, keyname):
        """Remove a specific key (row) from the database table."""
        self.dbmodelclass.delete_bykey({'keyname':keyname})


    def db_loadkey(self, keyname):
        """Load a specific key (row) from the database table and unserialize it into self.settingdict[keyname]."""
        # lookup row in database
        modelobj = self.dbmodelclass.find_one_bykey({'keyname':keyname})
        if (modelobj == None):
            propdict = {}
        else:
            propdict = modelobj.get_settingdict_unserialized()
        # set it
        self.settingdict[keyname] = propdict


    def db_savekey(self, keyname):
        """Serialize and then save self.settingdict[keyname] into the appropriate database row."""
        # we want to add a new row OR replace an existing one
        # ATTN: ideally we want to prevent against the rare case of someone else deleting the row as we are modifying it for save
        # so for now we load, change, save; but later we might want to use a db atomic update
        #
        self.db_lock([keyname])
        try:
            # try to load it first
            modelobj = self.dbmodelclass.find_one_bykey({'keyname':keyname})
            # if not found, create a new one
            if (modelobj == None):
                modelobj = self.dbmodelclass.new()
            # now modify it with new values
            modelobj.keyname = keyname
            modelobj.set_settingdict_serialize(get_value_from_dict(self.settingdict, keyname, None))
            # and save it
            modelobj.save()
        except Exception as exp:
            raise exp
        finally:
            self.db_unlock()



    def db_loadallkeys(self):
        """Load all database rows and unserialize into self.settingdict."""
        # load all into memory
        modelobjs = self.dbmodelclass.find_all()
        # clear current dictionary
        self.settingdict = {}
        # convert all
        for modelobj in modelobjs:
            #print "DEBUGGING All ONE modelobj = "+str(modelobj)
            keyname = modelobj.keyname
            self.settingdict[keyname] = modelobj.get_settingdict_unserialized()
































class MewloSettingsDb_Dynamic(MewloSettingsDb):
    """
    Derived version of MewloSettingsDb which dynamically creates a database model class on the fly to use, or which can have one passed into it
    An example of how you might use this, from old site construct:
        # database classes
        DEF_DBCLASSNAME_PackSettings = 'DbModel_Settings_Pack'
        DEF_DBTABLENAME_PackSettings = 'settings_pack'
        self.createappendcomp('packsettings', mdbsettings.MewloSettingsDb_Dynamic, dbmodelclassname=mconst.DEF_DBCLASSNAME_PackSettings, dbmodeltablename=mconst.DEF_DBTABLENAME_PackSettings)
        or
        self.createappendcomp('packsettings', mdbsettings.MewloSettingsDb_Dynamic, dbmodelclass=mdbsettings_pack.MewloDbModel_Settings_Pack)
    """


    def __init__(self, mewlosite, debugmode, dbmodelclassname = None, dbmodeltablename = None, dbmodelclass = None):
        # parent constructor
        super(MewloSettingsDb_Dynamic, self).__init__(mewlosite, debugmode)
        # record the class name we use and clear some values
        self.dbmodelclassname = dbmodelclassname
        self.dbmodeltablename = dbmodeltablename
        self.dbmodelclass = dbmodelclass

    def buildset_dbmodelclass(self):
        """Can be overridden by derived classes, by default uses class var."""
        # create dynamic class
        # if already set, then there is nothing to do
        if (self.dbmodelclass != None):
            return self.dbmodelclass
        self.dbmodelclass = self.mewlosite.comp('dbmanager').create_derived_dbmodelclass(self, mdbmodel_settings.MewloDbModel_Settings, self.dbmodelclassname, self.dbmodeltablename)


