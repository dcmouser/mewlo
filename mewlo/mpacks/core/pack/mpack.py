"""
mpack.py
Works with packmanager.py to support our pack/extension/addon system
"""


# mewlo imports
from ..helpers.misc import readfile_asjson, compare_versionstrings_isremotenewer, strvalnone
from ..eventlog.mevent import EventList, EFailure, EWarning, EInfo
from ..eventlog.mexceptionplus import ExceptionPlus
from ..helpers.webhelp import download_file_as_jsondict, download_file_to_file

# python imports
import json
import os




class MewloPack(object):
    """
    The MewloPack class represents a mewlo "pack" aka extension/plugin/addon/component.
    It is *not* the same as a Python "pack".
    All code (both core builtin code and 3rd party extensions/plugins) is always represented/supervised/versioned by one and only one mewlo pack.
    The MewloPack class exposes author and version info about a pack, supports online, version checking, database updating, dependency chains, etc.

    It is actually a fairly light-weight structure that:
        * loads a json info file with information about the "addon pack".
        * dynamically loads(imports) a python code module specified by the json info file.
        * dynamically instantiates a PackPayload object from the above python code module.
    It is actually the PackPayload object that, once instantiated, does the work of the addon.
    So, the right way to think of a Pack is as the bridge middleman responsible for instantiating a PackPayload addon.
    One reason we use this middleman object is so that we can instantiate (just) the middleman wrapper around the json info file, even when the addon is DISABLED.
    In this way, we can have instantiated MewloPack objects even for missing/disabled MewloPackPayloads.
    Additional features that the Pack class provides:
        * displaying addon info, version info, update checking, etc.
        * handles dependency checking, etc.
    A MewloPack also keeps an eventlist of any warnings or errors encountered while trying to instantiate the PackPayload.
    If an addon cannot be located/loaded/etc., the error information will be stored in this eventlist, and the addon will be disabled.
    """

    # class constants
    DEF_INFOFIELD_isrequired = 'isrequired'
    DEF_INFOFIELD_requires = 'requires'
    DEF_INFOFIELD_uniqueid = 'uniqueid'
    DEF_INFOFIELD_requiredpacks = 'packs'
    DEF_INFOFIELD_codefile = 'codefile'
    DEF_INFOFIELD_codeclass = 'codeclass'
    DEF_INFOFIELD_url_version = 'url.version'
    DEF_INFOFIELD_url_download = 'url.download'
    DEF_INFOFIELD_version = 'version'
    DEF_INFOFIELD_versiondate = 'versiondate'
    DEF_INFOFIELD_versioncritical = 'versioncritical'


    def __init__(self, packmanager, filepath):
        # keep pointer to pack manager
        self.packmanager = packmanager
        # found info (json) file defining the pack
        self.infofilepath = filepath
        # dictionary acquired from info file
        self.infodict = None
        # imported module of code
        self.codemodule_path = ''
        self.codemodule = None
        self.packpayload = None
        #
        self.readytoloadcode = False
        self.readytorun = False
        self.enabled = False
        self.enabledisablereason = "n/a"
        self.hasfailedstartup = True
        #
        self.eventlist = EventList()
        self.clear_updateinfo()


    def clear_eventlist(self):
        self.eventlist.clear()

    def appendevent(self, event):
        if (event != None):
            self.eventlist.append(event)

    def get_eventlist(self):
        return self.eventlist

    def clear_updateinfo(self):
        self.clear_eventlist()
        self.update_webfiles_needupdate = None
        self.update_database_needupdate = None
        self.update_webfiles_iscritical = None


    def get_uniqueid(self):
        return self.get_ourinfofile_property(MewloPack.DEF_INFOFIELD_uniqueid,'[uniqueid_not_specified]')

    def get_infofilepath(self):
        return self.infofilepath

    def do_enabledisable(self, mewlosite, flag_enable, reason, eventlist):
        """
        Set the disabled flag for the pack.  If False than the code for the pack will not be loaded and run.
        return None on success, or failure on error.
        """
        retv = None
        alreadyenabled = self.enabled

        # do stuff on change of state
        if (alreadyenabled == flag_enable):
            # nothing to do, it's already where we want it
            pass
        elif (flag_enable):
            # we want to enable this pack that is currently not enabled
            # ATTN: todo - do we want to OVERRIDE/IGNORE any settings that say to disable this pack when we are told to explicitly enable it? I say yes.
            retv = self.startup(mewlosite, eventlist)
        elif (not flag_enable):
            # we want to disable this pack that is currently enabled
            retv = self.shutdown()
        # change state on absence of error
        if (retv==None):
            self.enabled = flag_enable
            self.enabledisablereason = reason
        # keep track of whether we are in the state we want to be in
        self.hasfailedstartup = (flag_enable != self.enabled)
        # return
        return retv



    def create_packpayload(self, packpay_class):
        """Create an appropriate child pack; subclasses will reimplement this to use their preferred child class."""
        obj = packpay_class(self)
        return obj



    def load_infofile(self):
        """Load the info file (json data) for this pack."""

        # init
        self.infodict = None
        self.readytoloadcode = False

        # read the json file and parse it into a dictionary
        self.infodict, failure = readfile_asjson(self.infofilepath, "Pack info file")
        if (failure == None):
            # set readytoloadcode true since the json parsed properly
            self.readytoloadcode = True
        else:
            # failed; add the error message to our eventlist, and continue with this pack marked as not useable
            self.appendevent(failure)
            # we could raise an exception immediately if we wanted from the failure
            if (True):
                raise ExceptionPlus(failure)



    def load_codemodule(self):
        """
        Import the codemodule associated with this pack.
        Return None on success or failure on error
        """

        # init
        self.codemodule = None
        self.codemodule_path = ''
        self.packpayload = None
        self.readytorun = False

        # get path to code module
        self.codemodule_path, failure = self.get_pathtocodemodule()
        if (failure == None):
            # ask pack manager to load the import from the path
            self.codemodule, failure = self.packmanager.loadimport(self.codemodule_path)

        if (failure == None):
            # if the import worked, instantiate the pack object from it
            failure = self.instantiate_packpayload()

        if (failure == None):
            # success so mark it as ready to run
            self.readytorun = True
        else:
            # failed; add the error message to our eventlist, and continue with this pack marked as not useable? or raise exception right away
            self.appendevent(failure)
            if (True):
                raise ExceptionPlus(failure)
        # return failure
        return failure


    def get_pathtocodemodule(self):
        """The info file for the pack should tell us what module file to import; we default to same name as info file but with .py"""

        # default module name
        path = self.infofilepath
        dir, fullname = os.path.split(path)
        name, ext = os.path.splitext(fullname)
        pathtocodemodule_default = name + '.py'
        # override with explicit
        pathtocodemodule = dir + '/' + self.get_ourinfofile_property(MewloPack.DEF_INFOFIELD_codefile, pathtocodemodule_default)
        # return it
        return pathtocodemodule, None



    def instantiate_packpayload(self):
        """Assuming we have imported the dynamic pack module, now create the pack object that we invoke to do work"""

        # init
        self.packpayload = None

        # module loaded in memory?
        if (self.codemodule == None):
            return EFailure("No code module imported to instantiate pack object from.")

        # object class defined in info dictionary?
        packpayload_classname = self.get_ourinfofile_property(MewloPack.DEF_INFOFIELD_codeclass, None)
        if (packpayload_classname == None):
            return EFailure("Pack info file is missing the 'codeclass' property which defines the class of the MewloPack derived class in the pack module.")

        # does it exist
        if (not packpayload_classname in dir(self.codemodule)):
            return EFailure("Pack class '{0}' not found in pack module '{1}'.".format(packpayload_classname, self.codemodule.__name__))

        # instantiate it
        try:
            packpay_class = getattr(self.codemodule, packpayload_classname)
            packpayload_obj = self.create_packpayload(packpay_class)
        except:
            return EFailure("Pack class object '{0}' was found in pack module, but could not be instantiated.".format(packpayload_classname))

        # always prepare it first
        failure = packpayload_obj.prepare(self.get_mewlosite().comp('packsettings'))
        if (failure != None):
            # failure to prepare, so we let it go and return the failure
            packpayload_obj = None
            return failure

        # save it for use
        self.packpayload = packpayload_obj
        # no failure returns None
        return None



    def get_ourinfofile_property(self, propertyname, defaultval=None):
        """Lookup property in our info dict and return it, or defaultval if not found."""
        return self.get_aninfofile_property(self.infodict,propertyname,defaultval)

    def get_aninfofile_property(self, infodict, propertyname, defaultval=None):
        """Lookup property in an info dict and return it, or defaultval if not found."""

        if (infodict == None):
            return defaultval
        if (propertyname in infodict):
            return infodict[propertyname]
        return defaultval



    def startup(self, mewlosite, eventlist):
        """Do any startup stuff."""
        if (self.update_webfiles_iscritical):
            # do not allow startup since there is a critical update available
            # ATTN: as the code is now, this never triggers because we dont check for web updates until AFTER this code runs
            return EFailure("Cannot enable/startup pack because a *critical* web update is available.")
        if (self.readytoloadcode):
            # load the code module
            failure = self.load_codemodule()
            if (failure!=None):
                return failure
            # we loaded the code, now lets see if it reports it needs a database update
            database_needupdate, failure = self.update_database_check()
            if (failure!=None):
                return failure
            if (database_needupdate):
                # cannot allow startup since it needs a database update
                return EWarning("Cannot start pack because it reports that it needs to run a database update first.")
            if (self.packpayload!=None):
                # ok we loaded the code, now we need to ask the code itself if its ready to run
                failure = self.packpayload.check_isusable()
                if (failure!=None):
                    return failure
                failure = self.packpayload.startup(mewlosite, eventlist)
                return failure
        # ATTN: do we want to throw an error/failure in this case where the code module is not ready to run?


    def shutdown(self):
        """Do any shutdown stuff."""
        if (self.packpayload!=None):
            self.packpayload.shutdown()
            # and now release the packpayload payload to garbage collection
            self.packpayload = None

    def get_mewlosite(self):
        return self.packmanager.get_mewlosite()














    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""

        outstr = " "*indent + "Pack '{0}' reporting in:\n".format(self.get_uniqueid())
        indent += 1
        #
        outstr += " "*indent + "Enabled: " + str(self.enabled) + " ("+self.enabledisablereason+").\n"
        #
        outstr += " "*indent + "Info dictionary: " + self.get_infofilepath() + ":\n"
        jsonstring = json.dumps(self.infodict, indent=indent+1)
        outstr += " "*indent + " '" + jsonstring + "'\n"
        #
        outstr += " "*indent + "Code module file: " + self.codemodule_path + "\n"
        #
        outstr += " "*indent + "Code module: "
        outstr += str(self.codemodule) + "\n"
        #
        outstr += " "*indent + "Pack object: "
        outstr += str(self.packpayload) + "\n"
        if (self.packpayload):
            outstr += self.packpayload.dumps(indent+1)
        #
        outstr += " "*indent + "Update check results:\n"
        outstr += " "*indent + " Web has newer version available? {0}\n".format(strvalnone(self.update_webfiles_needupdate,'not checked'))
        if (self.update_webfiles_needupdate == True):
            outstr += " "*indent + "  Web update is critical? {0}\n".format(strvalnone(self.update_webfiles_iscritical,'not checked'))
        outstr += " "*indent + " Database needs update? {0}\n".format(strvalnone(self.update_database_needupdate,'not checked'))
        outstr += self.eventlist.dumps(indent+1)
        #
        return outstr

















    def get_hasfailedstartup(self):
        """Return true if the pack has failed to startup for any reason (needs update, etc.)."""
        return self.hasfailedstartup
































    def updatecheck(self):
        """
        Check pack for updates.
        Note this covers not just web updates available, but database updates needed.
        Division of labor:
            We (the MewloPack wrapper) can do a web check
            but we have to ask the MewloPackPayload to do the database check.
        """

        # clear eventlist and needupdate flags
        self.clear_updateinfo()

        # first check for web file update available
        self.update_webfiles_needupdate, self.update_webfiles_iscritical, webinfodict, failure = self.updatecheck_checkfornewfiles()
        if (failure != None):
            # error
            self.appendevent(failure)
            return self.update_webfiles_needupdate, failure

        if (self.update_webfiles_needupdate):
            # new web version available so stop here and say yes
            return True, None

        # database check
        self.update_database_needupdate, failure = self.update_database_check()
        return self.update_database_needupdate, failure



    def update_database_check(self):
        """
        Check if there needs to be a database update for this module.
        """
        if (self.packpayload!=None):
            # no file update available, so check for database update
            self.update_database_needupdate, failure = self.packpayload.updatecheck_checkdatabase()
            self.appendevent(failure)
            return self.update_database_needupdate, failure
        # no pack object available -- so do nothing (it should error elsewhere)
        return False, None


    def updaterun(self):
        """
        Check pack for updates.
        Note this covers not just web updates available, but database updates needed.
        Division of labor:
            We (the MewloPack wrapper) can do a web check
            but we have to ask the MewloPackPayload to do the database check.
        :return: tuple (didupdate, failure)
        """

        # clear eventlist and needupdate flags
        self.clear_updateinfo()

        # first check for web file update available
        self.update_webfiles_needupdate, self.update_webfiles_iscritical, webinfodict, failure = self.updatecheck_checkfornewfiles()
        if (failure != None):
            self.appendevent(failure)
            return self.update_webfiles_needupdate, failure

        if (self.update_webfiles_needupdate):
            # ok we want to download and apply the web file update
            # first we make a merged version of the info dict, overriding local with remote -- this allows remote to override download location IFF it wants
            mergedinfodict = self.infodict.copy()
            mergedinfodict.update(webinfodict)
            # now get download url
            remotedownloadurl = self.get_aninfofile_property(mergedinfodict, MewloPack.DEF_INFOFIELD_url_download, None)
            # download it and install it
            failure = self.update_download_and_install(mergedinfodict, remotedownloadurl)
            if (failure != None):
                self.appendevent(failure)
                return False, failure
            # we successfully ran a file upodate so we will NOT drop down and check for database update (until next restart)
            return True, None

        # new version not available on web; check if a database update is needed
        if (self.packpayload!=None):
            didupdate, failure = self.packpayload.updaterun_database()
            if (failure != None):
                self.appendevent(failure)
                return False, failure
            return didupdate, None

        # nothing done
        return False, None



















    def updatecheck_checkfornewfiles(self):
        """
        Check web for new files available, and check our download staging directory for these?
        The different components here are:
            1. web check at url specified in our info file for an online version check
            2. web check at some central repository based on uniqueid
            3. check in local "to-install" folder
            4. identification of the file to download
        :return: tuple (isneweravail, isupdatecritical, webdictionary, failure)
        """

        # download web version info json file and parse it
        webinfodict, failure = self.download_versioninfodict()
        if (failure != None):
            return False, False, webinfodict, failure

        # ok let's get the remote version string (and local one)
        localversion = self.get_ourinfofile_property(MewloPack.DEF_INFOFIELD_version, None)
        remoteversion = self.get_aninfofile_property(webinfodict, MewloPack.DEF_INFOFIELD_version, None)
        remotedate  = self.get_aninfofile_property(webinfodict, MewloPack.DEF_INFOFIELD_versiondate, 'undated')
        isremoteversioncritical = self.get_aninfofile_property(webinfodict, MewloPack.DEF_INFOFIELD_versioncritical, False)
        if (remoteversion==None):
            # error, no remote version info
            versionfile_url = self.get_ourinfofile_property(MewloPack.DEF_INFOFIELD_url_version, None)
            failure = EFailure("No remote version specified in remote info file ({0}).".format(versionfile_url))
            return False, False, webinfodict, failure

        # ok we have local and remote version strings, let's compare
        isneweravail, failure = compare_versionstrings_isremotenewer(localversion, remoteversion)
        if (failure != None):
            return isneweravail, isremoteversioncritical, webinfodict, failure

        # no newer version available?
        if (not isneweravail):
            # should we log a non-error message saying no new version vailable?
            self.appendevent(EInfo("Online check confirms latest version is installed ({0} - {1}).".format(localversion,remotedate)))
            return False, False, webinfodict, None

        # new version is available, add event saying so (note we dont RETURN this message as a failure, we add it to our event log, because its not an error)
        if (isremoteversioncritical):
            # the remote version is labeled as a critical version -- we don't want to let the current version run
            reasonstr = "New *CRITICAL* version ({0} - {1}) is available online.".format(remoteversion,remotedate)
            self.appendevent(EInfo(reasonstr))
            # if the pack is ALREADY enabled, we DISABLE it and set it as being blocked from running
            if (self.enabled):
                self.do_enabledisable(self.get_mewlosite(), False, reasonstr, self.eventlist)
                self.hasfailedstartup = True
        else:
            # normal optional new version
            self.appendevent(EInfo("Newer version ({0} - {1}) is available online.".format(remoteversion,remotedate)))

        # new version available and no error
        return True, isremoteversioncritical, webinfodict, None




    def download_versioninfodict(self):
        """
        Download and parse web info file
        :return: tuple (webdictionary, failure)
        """
        versionfile_url = self.get_ourinfofile_property(MewloPack.DEF_INFOFIELD_url_version, None)
        if (versionfile_url == None):
            failure = EFailure("No url to check online for updates specified ('url.version').")
            return None, failure

        webinfodict, failure = download_file_as_jsondict(versionfile_url)
        if (failure != None):
            return False, failure

        #success
        #print "ATTN: downloaded webinfo dict from {0} as:".format(versionfile_url) + str(webinfodict)
        return webinfodict, None











    def update_download_and_install(self, mergedinfodict, remotedownloadurl):
        """Download update file and install it."""
        # generate a desired local filename
        # ATTN: TO FIX -- for now im just testing with a hardcoded path
        update_download_dir = 'E:/WebsiteHttp/mewlo/mewlo/updates/pending'
        update_download_fname = 'test.zip'
        #
        update_download_filepath = update_download_dir + '/' + update_download_fname
        downloadedfilepath, failure = download_file_to_file(remotedownloadurl, update_download_filepath)
        if (failure != None):
            return failure

        # downloaded, now install
        self.appendevent(EInfo("Downloaded update ({0}), ready to install.".format(downloadedfilepath)))

        # ATTN: not finished yet
        failure = EFailure("New version downloaded but not installed, because installation of new pack downloads not supported yet.")
        return failure

        return None









    def update_nicestring(self, msg=''):
        """Return a warning with info about pack id."""
        msg = "Pack '{0}' with info file '{1}': ".format(self.get_uniqueid(), self.get_infofilepath()) + msg
        return msg

    def updatemessage(self, msg):
        """Return a warning with info about pack id."""
        msg = self.update_nicestring(msg)
        return EInfo(msg)


