"""
mpackmanager.py
This file supports discovery and loading of modules by path and filename pattern

Note that our term "pack" here is not referring to python packs (directories).

The pack system here is made up of 3 classes:

    * MewloPackManager - holds a list of Packs.
    * MewloPack - a thin wrapper around a pack object.
    * MewloPackWorker - the object that will be subclassed to do real work.

The MewloPack is the thing that is autocreated on discovery of a .json definition file.
It will be instantiated even if this extension is disabled.

The PackWorker is only instantiated when the extension is enabled.

When you code a new plugin/extension, you ONLY create a derived MewloPackWorker class.
The MewloPack is created by the manager.

"""


# mewlo imports
from ..helpers.callables import importmodule_bypath
from ..eventlog.mevent import EFailure, EDebug, EventList
from ..helpers.misc import get_value_from_dict, append_text
from mpack import MewloPack
from ..manager import manager
from ..setting.msettings import MewloSettings
from ..const.mconst import MewloConst as siteconst

# python imports
import imp
import fnmatch
import os













class MewloPackManager(manager.MewloManager):
    """
    The PackManager is a class that can be used to dynamically find modules by path and filename pattern.  It manages a collection of Pack objects that represent addonsm, etc.
    It's useful for plugin-discovery type things.
    """

    # class constants
    description = "Manages all 'MewloPacks' which are collections of files that can be updated"
    typestr = "core"



    # class-wide dictionary of module imports, to avoid multiple dynamic-code-importing
    classwide_packmodules = {}


    def __init__(self, mewlosite, debugmode):
        # stuff
        super(MewloPackManager,self).__init__(mewlosite, debugmode)
        self.dirlist = []
        self.infofilepaths = []
        self.filepatternsuffix = ''
        self.setuptools_entrypoint_groupname = ''
        self.packsettings = {}
        self.default_packsettings = {}
        self.flag_loadsetuptoolspacks = True
        # pack collection
        self.packs = []
        self.packhash = {}
        # set file pattern of mewlo pack files
        self.set_filepatternsuffix(siteconst.DEF_PACK_filepatternsuffix)
        # set setuptools entrypoint groupname
        self.set_setuptools_entrypoint_groupname('mewlo.packs')



    def startup(self, eventlist):
        """Any initial startup stuff to do?"""
        super(MewloPackManager,self).startup(eventlist)
        # discover the packs in the pack directories
        self.discover_packs(eventlist)
        # startup packs right away?
        if (True):
            self.startup_packs(eventlist)



    def startup_packs(self, eventlist):
        """Startup packs.  We do this separately from normal startup() because we may want to check for updates first."""
        for pack in self.packs:
            failure = self.startup_pack_auto(self.mewlosite, pack, eventlist)
            if (failure != None):
                # if we get a hard failure here, we add it to our list of failures, and to the eventlist
                eventlist.append(failure)



    def shutdown(self):
        """Shutdown the packs."""
        super(MewloPackManager,self).shutdown()
        for pack in self.packs:
            pack.shutdown()






    def set_directories(self, dirlist):
        self.dirlist = dirlist

    def set_filepatternsuffix(self, filepatternsuffix):
        self.filepatternsuffix = filepatternsuffix

    def set_setuptools_entrypoint_groupname(self, setuptools_entrypoint_groupname):
        self.setuptools_entrypoint_groupname = setuptools_entrypoint_groupname

    def set_packsettings(self, packsettings):
        self.packsettings = packsettings

    def set_default_packsettings(self, default_packsettings):
        self.default_packsettings = default_packsettings

    def set_flag_loadsetuptoolspacks(self, val):
        self.flag_loadsetuptoolspacks = val


    def create_pack(self, filepath):
        """Create an appropriate child pack."""
        return MewloPack(self, filepath)


    def createadd_pack_frominfofile(self, infofilepath, eventlist):
        """Given a path to an infofile, create a pack from it."""
        pkg = self.create_pack(infofilepath)
        if (pkg != None):
            self.packs.append(pkg)
            # load the info file related to it
            pkg.load_infofile()
            # now add it to hash
            apackid = pkg.get_ourinfofile_property(siteconst.DEF_PACK_INFOFIELD_uniqueid)
            if (apackid in self.packhash):
                # duplicate pack id
                failure = EFailure("Two packs found with same .json uniqueid ('{0}' vs '{1}').".format(self.packhash[apackid].get_infofilepath(),pkg.get_infofilepath()))
                eventlist.append(failure)
            else:
                self.packhash[apackid] = pkg
        else:
            failure = EFailure("Failed to create_pack from .json infofile '{0}'.".format(infofilepath))
            eventlist.append(failure)
        return pkg





    def get_mewlosite(self):
        return self.mewlosite




    def discover_packs(self, eventlist):
        """Scan all pack directories and discover packs."""
        # init
        filepattern = self.calc_packinfofile_pattern()
        # remove any EXISTING packs and clear our list of infofilepaths
        self.packs = []
        self.infofilepaths = []
        # add list of directories to scan
        for dirpath in self.dirlist:
            self.infofilepaths += self.findfilepaths(dirpath, filepattern)
        # add any from setup tools entrypoint loading
        if (self.flag_loadsetuptoolspacks):
            self.infofilepaths += self.discover_setuptools_entrypoints_infofilepaths()
        # now for each file, create a pack from it
        for filepath in self.infofilepaths:
            # create the pack wrapper from the file
            pkg = self.createadd_pack_frominfofile(filepath, eventlist)





    def calc_packinfofile_pattern(self):
        """Given self.filepatternsuffix we create the file match pattern that describes the json info files we need to look for."""
        return '*_' + self.filepatternsuffix + '.json'


    def findfilepaths(self, dirpath, filepattern):
        """Find recursive list of filepaths matching pattern."""
        filepaths = []
        for path, dirs, files in os.walk(os.path.abspath(dirpath)):
            for filename in fnmatch.filter(files, filepattern):
                filepaths.append(os.path.join(path, filename))
        return filepaths







    def discover_setuptools_entrypoints_infofilepaths(self):
        """Discover any setuptools based entry-point plugins that are exposing their info."""
        if (self.setuptools_entrypoint_groupname == ''):
            return []
        # init
        infofilepaths = []
        filepattern = self.calc_packinfofile_pattern()
        #
        # ok we found some so let's try
        import pkg_resources
        import os
        #
        for entrypoint in pkg_resources.iter_entry_points(group=self.setuptools_entrypoint_groupname):
            # Ok get the entrypoint details
            entrypoint_fullname = entrypoint.name
            entrypoint_basename = entrypoint_fullname.split('.')[0]
            entrypoint_obj = entrypoint.load()
            # if entrypoint_obj is a callable, call it to get data, otherwise it IS the data alread
            if (hasattr(entrypoint_obj, '__call__')):
                entrypoint_data = entrypoint_obj()
            else:
                entrypoint_data = entrypoint_obj
            # debug
            #print "---------> GOT AN ENTRYPOINT OF "+str(entrypoint_obj)+" named: "+entrypoint_fullname + " (" + entrypoint_basename + ") with data: "+str(entrypoint_data)+"\n"
            # ok now let's handle it
            if (entrypoint_basename == 'infofiles'):
                # it's giving us info file (or list of them), so we append to filepaths
                if (isinstance(entrypoint_data, basestring)):
                    entrypoint_data = [ enrtypoint_data ]
                infofilepaths += entrypoint_data
            elif (entrypoint_basename == 'infofiledirs'):
                # it's giving us a directory (or list of them) to scan, so scan and add all in their
                if (isinstance(entrypoint_data, basestring)):
                    entrypoint_data = [ entrypoint_data ]
                for apath in entrypoint_data:
                    infofilepaths += self.findfilepaths(apath, filepattern)
            elif (entrypoint_basename == 'moduleforpath'):
                # it's giving us a module (or list of them) to resolve directories from and then treat as infofiledirs
                if (not hasattr(entrypoint_data, '__iter__')):
                    entrypoint_data = [ entrypoint_data ]
                for amod in entrypoint_data:
                    apath = os.path.abspath(os.path.dirname(amod.__file__))
                    infofilepaths += self.findfilepaths(apath, filepattern)
            else:
                # error bad directive in entry_point
                emsg = "While trying to load advertised setuptools entrypoints for Mewlo plugins (group='"+self.setuptools_entrypoint_groupname+"'), encountered an enrtypoint key value '"+entrypoint_fullname+"' that was not understood."
                emsg += " Full entrypoint line: "+str(entrypoint)+"."
                emsg += " Note that this line causing the error will most likely be located in a python EGG of an INSTALLED site-pack; in the egg's setup.py or compiled into entry_points.txt."
                raise Exception(emsg)
        #
        return infofilepaths
















    def loadimport(self, path):
        """Dynamically load an importbypath (or returned cached value of previous import)."""
        dynamicmodule = None

        # not in our cache? then we have to load it
        if (not path in MewloPackManager.classwide_packmodules):
            # first we check if path is blank or does not exist
            if (path == ''):
                return None, EFailure("Failed to load import by path '{0}', because a blank path was specified.".format(path))
            elif (not os.path.isfile(path)):
                return None, EFailure("Failed to load import by path '{0}', because that file does not exist.".format(path))
            else:
                # then load it dynamically
                dynamicmodule, failure = importmodule_bypath(path)
                if (failure != None):
                    return None, failure

            # now add it to our class-wide cache, so we don't try to reload it again
            MewloPackManager.classwide_packmodules[path] = dynamicmodule

        # return it
        return MewloPackManager.classwide_packmodules[path], None






    def get_settings_forpack(self, packid):
        """Given a pack id, lookup its settings."""
        retv = get_value_from_dict(self.packsettings,packid,{})
        return retv



    def startup_pack_auto(self, mewlosite, pack, eventlist):
        """Before we instantiate a pack, we preprocess it using our settings, which may disable/enabe them."""
        packid = pack.get_ourinfofile_property(siteconst.DEF_PACK_INFOFIELD_uniqueid)
        # let's see if user WANTS this pack enabled or disabled based on settings
        (flag_enable, reason) = self.want_enable_pack(pack, eventlist)
        # if they want it enabled, lets see if it meets initial dependency check if not, its a failure
        if (flag_enable):
            (dependencies_met, failurereason) = self.check_pack_dependencies(pack, None, [])
            if (not dependencies_met):
                # dependency fail, disable it and return the dependency error
                flag_enable = False
                pack.do_enabledisable(mewlosite, flag_enable, reason, eventlist)
                return EFailure(failurereason)
        elif (pack.get_ourinfofile_property(siteconst.DEF_PACK_INFOFIELD_isrequired)):
            # required packd is disabled, that's an error
            failurereason = "required pack '{0}' is {1}; mewlo cannot run".format(packid,reason)
            return EFailure(failurereason)
        failure = pack.do_enabledisable(mewlosite, flag_enable, reason, eventlist)
        return failure



    def want_enable_pack(self, pack, eventlist):
        """Do settings say to disable this pack? Return tuple of (flag_enable, reasonstring)."""
        packid = pack.get_ourinfofile_property(siteconst.DEF_PACK_INFOFIELD_uniqueid)
        #
        reason = "n/a"
        # get any settings for the pack
        packsettings = self.get_settings_forpack(packid)
        flag_enable = get_value_from_dict(packsettings,siteconst.DEF_SETTINGNAME_isenabled)
        # is the pack REQUIRED?
        if (pack.get_ourinfofile_property(siteconst.DEF_PACK_INFOFIELD_isrequired) and flag_enable != False):
            # set to enable if enabled explicitly or nothing specified
            reason = "required pack"
            flag_enable = True
        elif (flag_enable==None):
            flag_enable = get_value_from_dict(self.default_packsettings, siteconst.DEF_SETTINGNAME_isenabled)
            reason = "default enable/disable state for packs"
        else:
           if (flag_enable):
                reason = "explicitly enabled in site settings"
           else:
                reason = "explicitly disabled in site settings"
        return (flag_enable, reason)



    def will_enable_pack_byid(self, packid, requirer, assumegoodlist):
        """Check if pack will be enabled, by id."""
        pack = self.findpack_byid(packid)
        if (pack==None):
            return (False,"Pack not found".format(packid))
        eventlist = []
        (flag_enable, reason) = self.want_enable_pack(pack, eventlist)
        if (flag_enable):
            (dependencies_met, reason) = self.check_pack_dependencies(pack, requirer, assumegoodlist)
            if (not dependencies_met):
                flag_enable = false
        return (flag_enable, reason)


    def check_pack_dependencies(self, pack, requirer, assumegoodlist):
        """
        Check whether this pack has its dependenices met.  Return tuple (dependencies_met, reasontext).
	    In the json file this looks like:
            "requires": {
			    "packs": ["mouser.mewlotestplug"]
		        },
        """
        reason = ""
        result = True
        packid = pack.get_ourinfofile_property(siteconst.DEF_PACK_INFOFIELD_uniqueid)
        if (requirer==None):
            requirer = "Pack '{0}'".format(packid)
        # is this pack already on our assumed good list? if so just return and and say good (this avoids circular dependencies)
        if (packid in assumegoodlist):
            return (True,"")
        # add this packid to our list of assumed good
        assumegoodlist.append(packid)
        # first get the list of what this pack requires
        requiredict = pack.get_ourinfofile_property(siteconst.DEF_PACK_INFOFIELD_requires)
        if (requiredict != None):
            # ok let's check for required PACKAGES (not python packs but our packs)
            requiredpacks = get_value_from_dict(requiredict, siteconst.DEF_PACK_INFOFIELD_requiredpacks)
            if (requiredpacks != None):
                # ok we need to check required packs
                # ATTN: TODO - we may want to check version infor here later
                for packid in requiredpacks:
                    (required_pack_enabled, thisreason) = self.will_enable_pack_byid(packid, requirer, assumegoodlist)
                    if (not required_pack_enabled):
                        result = False
                        thisreason = "{0} failed to load because it depends on pack '{1}', which is not enabled because: ".format(requirer, packid) + thisreason
                        reason = append_text(reason, thisreason, " ;")
        # if we fell down to here, all requirements are met
        return (result, reason)




    def findpack_byid(self, packid):
        """Return the pack object for the pack specified by id, or None if not found."""
        if (packid in self.packhash):
            return self.packhash[packid]
        # not found in hash, we assume hash is up to date
        return None











    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "PackManager reporting in ({0} packs found).\n".format(len(self.packs))
        outstr += self.dumps_description(indent+1)
        indent += 1
        outstr += " "*indent + "Directories scanned:\n"
        for dirpath in self.dirlist:
            outstr += " "*indent + " "+dirpath + "\n"
        outstr += " "*indent + "Also scanning installed mewlo python-setuptools-based packs: {0}.\n".format(str(self.flag_loadsetuptoolspacks))
        outstr += " "*indent + "Info files found:\n"
        for dirpath in self.infofilepaths:
            outstr += " "*indent + " "+dirpath + "\n"
        outstr += "\n"
        #
        indent += 1
        for pack in self.packs:
            outstr += pack.dumps(indent+1) + "\n"
        return outstr





    def is_readytoserve(self):
        """Check if there were any site prep errors, OR if any packs report they are not ready to run (need update, etc.)."""
        isreadytoserve = True
        for pack in self.packs:
            # is this pack such that we can't serve?
            if (pack.get_hasfailedstartup()):
                isreadytoserve = False
        return isreadytoserve























    def updatecheck_allpacks(self):
        """
        Check all packs for updates.  The packs themselves will store details about update check results.
        Note this covers not just web updates available, but database updates needed.
        """
        for pack in self.packs:
            pack.updatecheck()


    def updaterun_allpacks(self):
        """
        Check all packs for updates.  The packs themselves will store details about update check results.
        Note this covers not just web updates available, but database updates needed.
        """
        for pack in self.packs:
            pack.updaterun()


    def get_allpack_events(self):
        """
        Get combined eventlist for all packs.
        We merge in fields about the pack so they are available for debugging.
        """
        alleventlist = EventList()
        for pack in self.packs:
            packfields = {'pack':pack.get_uniqueid(), 'pack_infofile':pack.get_infofilepath()}
            packeventlist = (pack.get_eventlist()).makecopy()
            packeventlist.mergefields_allevents(packfields)
            alleventlist.appendlist(packeventlist)
        return alleventlist









