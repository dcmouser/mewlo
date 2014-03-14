"""
mcache.py
Cache class.
"""


# mewlo imports
from ..manager import manager
from ..setting.msettings import MewloSettings
from ..eventlog.mevent import EFailure, EException
from ..constants.mconstants import MewloConstants as mconst

# python library imports
from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE

# python imports





class MewloCacheManager(manager.MewloManager):
    """Lightweight cache object that just wraps a 3rd party library.
    So this class just exposes an API, derived classes do the work."""

    # class constants
    description = "Provides an API for cache system"
    typestr = "core"
    regiondict = {}


    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloCacheManager,self).__init__(mewlosite, debugmode)







    def addcache_region(self, key, regionobj):
        """Add a region object to our dictionary cache."""
        self.regiondict[key]=regionobj

    def lookup_cachedregion(self, key):
        """Lookup region in our dictionary cache."""
        if (key in self.regiondict):
            return self.regiondict[key]
        return None

    def convertregion(self, region):
        """Return a region object -- if a string is passed, look up the region by string."""
        if (isinstance(region,basestring)):
            return self.lookup_cachedregion(region)
        return region

























class MewloCacheManager_DogPile(MewloCacheManager):
    """Dogpile derived cache."""

    # class constants
    description = "Provides an API for cache system, using Dogpile cache engine"
    typestr = "core"


    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloCacheManager_DogPile,self).__init__(mewlosite, debugmode)
        self.needs_startupstages([mconst.DEF_STARTUPSTAGE_assetstuff])


    def startup_prep(self, stageid, eventlist):
        """
        This is invoked by site strtup, for each stage specified in startup_stages_needed() above.
        """
        super(MewloCacheManager_DogPile,self).startup_prep(stageid, eventlist)
        if (stageid == mconst.DEF_STARTUPSTAGE_assetstuff):
            # create a test region
            self.make_region('mtestregion')









    # helpers

    def is_emptyval(self, val):
        return val == NO_VALUE

    def getd(self, region, key, defaultval=None, expiration_time=None, ignore_expiration=False):
        """Return a value from the cache, based on the given key."""
        region = self.convertregion(region)
        val = region.get(key, expiration_time, ignore_expiration)
        if (val == NO_VALUE):
            return defaultval
        return val






    # direct wrappers from dogpile API
    #see http://dogpilecache.readthedocs.org/en/latest/usage.html#recipes

    def make_region(self, regionname):
        region = make_region(name=regionname).configure(
            "dogpile.cache.memory",
        )
        # add to cache
        self.addcache_region(regionname, region)
        # return it
        return region


    def delete(self, region, key):
        """Remove a value from the cache."""
        region = self.convertregion(region)
        return region.delete(key)

    def delete_multi(self, region, keys):
        """Remove multiple values from the cache."""
        region = self.convertregion(region)
        return region.delete_multi(keys)

    def get(self, region, key, expiration_time=None, ignore_expiration=False):
        """Return a value from the cache, based on the given key."""
        region = self.convertregion(region)
        return region.get(key, expiration_time, ignore_expiration)

    def get_multi(self, region, keys, expiration_time=None, ignore_expiration=False):
        """Return multiple values from the cache, based on the given keys."""
        region = self.convertregion(region)
        return region.get_multi(keys, expiration_time, ignore_expiration)

    def get_or_create(self, region, key, creator, expiration_time=None, should_cache_fn=None):
        """Return a cached value based on the given key."""
        region = self.convertregion(region)
        return region.get_or_create(key, creator, expiration_time, should_cache_fn)

    def get_or_create_multi(self, region, keys, creator, expiration_time=None, should_cache_fn=None):
        """Return a sequence of cached values based on a sequence of keys."""
        region = self.convertregion(region)
        return region.get_or_create_multi(keys, creator, expiration_time, should_cache_fn)

    def invalidate(self, region, hard=True):
        """Invalidate this CacheRegion."""
        region = self.convertregion(region)
        return region.invalidate(hard)

    def set(self, region, key, value):
        """Place a new value in the cache under the given key."""
        region = self.convertregion(region)
        return region.set(key, value)

    def set_multi(self, region, mapping):
        """Place new values in the cache under the given keys."""
        region = self.convertregion(region)
        return region.set_multi(mapping)

