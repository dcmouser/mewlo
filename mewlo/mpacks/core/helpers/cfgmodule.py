"""
cfgmodule.py
Helper class that can load multiple python modules and smartly return an attribute from them in precedence order
"""


# mewlo imports
import callables

# python imports





class MCfgModule(dict):
    """Lookup values smartly in one of multiple python modules, found dynamically."""

    def __init__(self):
        self.configimports = []

    def load_configfiles(self, configname, pkgdirimp_config):
        """Load the config files (some may not be found), in order of precedence, with default last."""
        self.configname = configname
        self.pkgdirimp_config = pkgdirimp_config
        if (self.pkgdirimp_config==None):
            return
        # load configname_secret, configname, default, in that order -- the order is key
        self.loadaddconfigfile(configname+'_secret')
        self.loadaddconfigfile(configname)
        self.loadaddconfigfile('default')

    def loadaddconfigfile(self, fname):
        """Load and add a config file module.  It's ok if it's missing"""
        try:
            cfgmodule = callables.find_module_from_dottedpath(self.pkgdirimp_config, fname)
        except ImportError as exception:
            #print "ATTN: WARNING could not find cfg module file '{0}' relative to config package '{1}'.".format(fname,str(self.pkgdirimp_config))
            return
        # found it, so add it
        #print "ATTN:DEBUG Added cfg module: '{0}'.".format(fname)
        self.configimports.append(cfgmodule)


    def get_value(self, key, defaultval=None):
        """Walk all of our imports and return first one that has the key."""
        for importobj in self.configimports:
            if (hasattr(importobj,key)):
                # found it
                return getattr(importobj,key)
        # not found
        return defaultval