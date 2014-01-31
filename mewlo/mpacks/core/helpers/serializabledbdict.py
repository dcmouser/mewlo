"""
serializabledbdict.py
This module contains classes to support a serializable dictionary for db use
"""


# helper imports
import misc

# python imports





class SerializeableDbDict(object):
    """Dictionary like object that is made for smart automatic serialization and unserialization to a database model."""


    def __init__(self):
        """Constructor."""
        self.serializedstring = None
        self.valuedict = {}
        self.isuptodate = True
        self.haschanged = False
        self.isunserialized = False



    def set_keyval(self, keyname, val):
        """Set a dictionary value -- no effect if value is same as existing."""
        self.unserialize_ifpending()
        if ((not keyname in self.valuedict) or (self.valuedict[keyname]!=val)):
            self.valuedict[keyname] = val
            self.aftermodify()

    def delete_keyval(self, keyname, val):
        """Remove a dictionary value -- no effect if value doesn't exist."""
        self.unserialize_ifpending()
        if (keyname in self.valuedict):
            del self.valuedict[keyname]
            self.aftermodify()

    def get_keyval(self, keyname, defaultval):
        """Get a dictionary value, or default if missing."""
        self.unserialize_ifpending()
        if (keyname in self.valuedict):
            return self.valuedict[keyname]
        else:
            return defaultval

    def aftermodify(self):
        """Called after a change has been made; we record that our serialized string is not up to date with dictionary, and that changes have occurred that need db saving."""
        self.isuptodate = False
        self.haschanged = True

    def update_serializestring_ifneeded(self):
        """Updates serialized string of dictionary IFF it needs updating (dictionary has changed since load)."""
        if (not self.isuptodate):
            # update it
            self.serializedstring = misc.serialize_forstorage(self.valuedict)
            # clear haschanged flag (leave dirty flag)
            self.isuptodate = True



    def get_haschanged(self):
        """Check this to see if we need to write out new serialization to database."""
        return self.haschanged

    def set_haschanged(self, val):
        """Force value of haschanged; could be called after saving to db."""
        self.haschanged = val

    def get_serializedstr(self):
        """Get the serialized version of the dictionary suitable for db saving; caller could call get_haschanged() first to see if it needs saving."""
        # update if needed
        self.update_serializestring_ifneeded()
        # return it
        return self.serializedstring

    def set_fromserializedstr(self, serializedstring):
        """Set the dictionary from the db string of it serialized; note we lazy unserialize so don't do that now"""
        self.serializedstring = serializedstring
        self.isunserialized = False
        self.haschanged = False

    def unserialize_ifpending(self):
        """Lazy unserialize."""
        if (self.isunserialized):
            return
        # unserialize it now
        self.valuedict = misc.unserialize_fromstorage(self.serializedstring,{})
        # set flag saying it's unserialized now
        self.isunserialized = True







class SerializeableDbDictCollection(object):
    """Collection of SerializeableDbDict."""


    def __init__(self, dictnamelist=None):
        """Constructor."""
        self.dicts = {}
        if (dictnamelist != None):
            self.init_dicts(dictnamelist)



    def init_dicts(self, dictnamelist):
        for dictname in dictnamelist:
            append(dictname,SerializeableDbDict())

    def append(self, dictname, thedict):
        self.dicts[dictname] = thedict

    def lookup_byname(self, dictname):
        if (not dictname in self.dicts):
            # not found
            return None
        return self.dicts[dictname]

    def get_alldicts(self):
        return self.dicts


    def set_keyval(self, dictname, keyname, val):
        lookup_byname(dictname).set_keyval(keyname, val)

    def get_keyval(self, dictname, keyname, defaultval):
        lookup_byname(dictname).get_keyval(keyname, defaultval)




