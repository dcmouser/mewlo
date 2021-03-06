"""
msiteaddon_account_mpack.py
This file "manages" the account site addon.

By "manage" we mean the following:

All code in mewlo, both the core code, and any 3rd party addons/plugins/extensions, is considered to be "managed" by a MewloPack.
The MewloPack provides information about the version of the code release and associated information suitable for doing online update checking,
 as well as author information, and dependency information between packs, etc.

So this Core_MewloPackWorker is the "manager" or owner of all core mewlo code.
It doesn't actually *do* anything -- but does describe and version the core code.

"""



# mewlo imports
from mewlo.mpacks.core.pack import mpackworker

# our imports
from mewlo.mpacks.site_addons.account import msiteaddon_account
import msiteaddon_group



class MewloPackWorker_SiteAddon_Group(mpackworker.MewloPackWorker):
    """
    """

    def __init__(self, pack):
        # parent constructor
        super(MewloPackWorker_SiteAddon_Group, self).__init__(pack)


    def startup(self, mewlosite, eventlist):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # return failure if any, or None on success
        retv = self.setup_everything(mewlosite, eventlist)
        return retv




    def setup_everything(self, mewlosite, eventlist):
        # called by Mewlo system when it's ready for us to do any setup stuff
        mewlosite.createappendcomp('groupaddon', msiteaddon_group.MewloSiteAddon_Group)
        return None


    def setup_databaseclasses(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        return None


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "MewloPackWorker_SiteAddon_Group reporting in.\n"
        return str

