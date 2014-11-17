"""
massetmanager.py
This module contains classes and functions to manage static file assets and aliases.

A MewloSite has a single MewloAssetManager, which it uses to help resolve any references with aliases.
A MewloAssetManager allows aliases to be set, and ensures all references to files and urls are resolved with these aliases.

"""


# mewlo imports
from ..helpers import misc
from ..manager import manager
from ..route import mroute, mroute_staticfiles
from ..controller import mcontroller_staticfiles
from ..constants.mconstants import MewloConstants as mconst

# python imports
import os
import copy
import distutils




class MewloAssetManager(manager.MewloManager):
    """The derived signal dispatcher."""

    # class constants
    description = "The asset manager handles static files that are served to user"
    typestr = "core"


    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloAssetManager,self).__init__(mewlosite, debugmode)
        # init
        self.needs_startupstages([mconst.DEF_STARTUPSTAGE_logstartup, mconst.DEF_STARTUPSTAGE_assetstuff])
        self.aliases = {}
        self.replacements_filepaths_static = {}
        self.asset_mounts = {}
        self.asset_sources = {}
        self.routegroup_mounting = None


    def startup_prep(self, stageid, eventlist):
        """
        This is invoked by site strtup, for each stage specified in startup_stages_needed() above.
        """
        super(MewloAssetManager,self).startup_prep(stageid, eventlist)
        if (stageid == mconst.DEF_STARTUPSTAGE_logstartup):
            # create any directories that settings tell us to
            self.makeuserdirs()
        if (stageid == mconst.DEF_STARTUPSTAGE_assetstuff):
            # set up replacement shadow for main mewlo directory? no, we will just do by pack
            # self.add_default_replacement_shadow_dirs()
            # mount our sources
            self.mountsources()




    def makeuserdirs(self):
        """User may have added directories they want us to create."""
        dirlist = self.mewlosite.settings.get_value(mconst.DEF_SETTINGSEC_make_dirs, [])
        for dirpath in dirlist:
            dirpath = self.resolve(dirpath,None)
            #print "ATTN:DEBUG site wants us to create dir '{0}'.".format(dirpath)
            misc.makedirectorypath(dirpath)




    #def set_alias_settings(self, aliases):
    #    """Assign the alias settings."""
    #    self.aliases = aliases


    def merge_aliases(self, mnamespace, aliases):
        """Merge in some aliases."""
        for (key,val) in aliases.iteritems():
            self.add_alias(mnamespace, key, val)


    def add_alias(self, mnamespace, aliasname, aliasval):
        """Add an alias."""
        hashkey = misc.mnamespacedid(mnamespace, aliasname)
        self.aliases[hashkey] = aliasval



    def calc_asset_varname(self, mnamespace, idname, varname):
        """Construct an asset varname with mnamespace.
        NOTE: If empty mnamespace, the varname will look like ::asset_idname_varname"""
        fullidvarname = 'asset_'+idname+'_'+varname
        return misc.mnamespacedid(mnamespace, fullidvarname)

    def calc_asset_varrep(self, mnamespace, idname, varname):
        """Construct an asset varname with mnamespace.
        NOTE: If empty mnamespace, the varname will look like ${::asset_idname_varname}"""
        return '${' + self.calc_asset_varname(mnamespace, idname, varname) + '}'













































    def resolve(self, text, mnamespace):
        """Resolve a string that could include $ aliases.  This is the central function that many places call."""
        if (text==None):
            return None
        if (not isinstance(text, basestring)):
            return text
        # ok resolve aliases -- for now we use a helper function to do the main work
        resolvedtext = misc.resolve_expand_string(text, self.aliases, mnamespace)
        # now we have a fully resolved string that may have contained some aliases
        return resolvedtext





    def resolve_filepath(self, text, mnamespace):
        """Call resolve THEN call replace_filepath."""
        resolvedtext = self.resolve(text, mnamespace)
        resolvedtext = self.replace_filepath(resolvedtext)
        #print "ATTN:DEBUG resolved '{0}' to '{1}'.".format(text, resolvedtext)
        return resolvedtext


    def resolve_filepath_canonical_noreplace(self, text, mnamespace):
        """Resolve string that could include $ aliases, AND THEN canonicalize it."""
        text = self.resolve(text, mnamespace)
        text = misc.canonicalize_filepath(text)
        return text





    # shortcuts that just call resolve() with some extra info

    def resolve_absolute_filepath(self, relpath, mnamespace):
        """Shortcut to resolve a filepath given a relative path."""
        return self.resolve_filepath('${sitefilepath}' + relpath, mnamespace)

    def resolve_absolute_url(self, relpath, mnamespace):
        """Shortcut to resolve a url given a relative path."""
        if (misc.isabsoluteurl(relpath)):
            return self.resolve(relpath, mnamespace)
        return self.resolve('${siteurl_absolute}' + relpath, mnamespace)

    def resolve_relative_url(self, relpath, mnamespace):
        """Shortcut to resolve a url that is relative to our server root."""
        if (misc.isabsoluteurl(relpath)):
            return self.resolve(relpath, mnamespace)
        return self.resolve('${siteurl_relative}' + relpath, mnamespace)





    def get_resolvedaliases_UNUSED(self, mnamespace):
        """Return a dictionary of resolved aliases; might be useful for templates."""
        # ATTN: Note that most aliases will not need resolving, but some may recurively include each other, that's why we have to do this
        # ATTN: Note that this could be quite slow unless we do it smartly -- would be nice to cache this result so that we don't have to recreate it each call
        # ATTN: TODO eliminate this function
        aliases = {}
        for key,val in self.aliases.iteritems():
            aliases[key] = misc.resolve_expand_string(val, self.aliases, mnamespace)
        return aliases






















































































    def add_default_replacement_shadow_dirs(self):
        """Add default mewlo replacement directory."""
        # a shadow directory allowing us to overide view and static files that are part of mewlo, under mewlo code
        orig_filedirpath = '${mewlofilepath}'
        replaceshadowpath = self.get_setting_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_replaceshadowpath, None)
        if (replaceshadowpath != None):
            # add shadow for main mewlo directory under subdirectory of replacedir
            new_filedirpath = replaceshadowpath + '/mewlo'
            self.add_replacement_shadowfiledir(orig_filedirpath, new_filedirpath, True)


    def add_outside_replacement_shadow_dirs(self,  orig_filedirpath, subdirid, flag_onlyifoutsidemain):
        """Add mewlo replacement directory -- IFF source is outside main mewlo path."""
        if (flag_onlyifoutsidemain):
            if (self.is_filepath_under_another(orig_filedirpath, '${mewlofilepath}')):
                # it's a subdirectory under main mewlo path, so do nothing
                #print "ATTN:DEBUG {0} is under {1} so not adding another shadow."
                return

        # a shadow subdirectory of a path outside main mewlo path, identified by an id
        replaceshadowpath = self.get_setting_subvalue(mconst.DEF_SETTINGSEC_config, mconst.DEF_SETTINGNAME_replaceshadowpath, None)
        if (replaceshadowpath != None):
            # add shadow for main mewlo directory under subdirectory of replacedir
            new_filedirpath = replaceshadowpath + '/' + subdirid
            self.add_replacement_shadowfiledir(orig_filedirpath, new_filedirpath, True)



    def is_filepath_under_another(self, filepath, potentialparent_filepath):
        filepath = self.resolve_filepath_canonical_noreplace(filepath, mnamespace=None)
        potentialparent_filepath = self.resolve_filepath_canonical_noreplace(potentialparent_filepath, mnamespace=None)
        if (filepath.startswith(potentialparent_filepath)):
            return True
        return False



    def add_replacement_filepath(self, orig_filepath, new_filepath):
        """Add a new mapping to replace a filepath."""
        # ATTN: note that we do not handle the case where the new_filepath has been previously rerouted to something else
        # first ensure all are in canonical format
        orig_filepath = self.resolve_filepath_canonical_noreplace(orig_filepath, mnamespace=None)
        new_filepath = self.resolve_filepath_canonical_noreplace(new_filepath, mnamespace=None)
        # now add it to our dictionary
        self.replacements_filepaths_static[orig_filepath] = new_filepath
        #print "ATTN:DEBUG adding asset replacement for '{0}' is '{1}'.".format(orig_filepath, new_filepath)


    def add_replacement_shadowfiledir(self, orig_filedirpath, new_filedirpath, flag_mkpath_root):
        """Traverse two shadow didrectories and add cases where there exists replacement files in the new filedirpath."""
        # first ensure all are in canonical format
        #print "ATTN: walking in add_replacement_shadowfiledir_static1 for '{0}' with filepath1 '{1}'.".format(orig_filedirpath, new_filedirpath)
        orig_filedirpath = self.resolve_filepath_canonical_noreplace(orig_filedirpath, mnamespace=None)
        new_filedirpath = self.resolve_filepath_canonical_noreplace(new_filedirpath, mnamespace=None)
        orig_filedirpath_len = len(orig_filedirpath)
        #print "ATTN: walking in add_replacement_shadowfiledir_static2 for '{0}' with filepath1 '{1}'.".format(orig_filedirpath, new_filedirpath)
        if (flag_mkpath_root):
            # make the root shadowed path to help user locate it, if it doesnt exist
            #print "ATTN:DEBUG making shadow source directory of {0}.".format(new_filedirpath)
            distutils.dir_util.mkpath(new_filedirpath)
        # now recurse deep in orig_filepath
        for (rootdir, subdirs, files) in os.walk(orig_filedirpath):
            # ok we have a candidate rootdir -- we want to get the relative path from orig_filedirpath
            if (rootdir.startswith(orig_filedirpath)):
                # remove it
                relativedir = rootdir[orig_filedirpath_len:]
            else:
                # error
                raise Exception("Walking directory '{0}' in add_replacement_shadowfiledir_static and unexpectedly got a dir that doesn't start with base directory; but instead is: '{1}'.".format(orig_filedirpath,rootdir))
            for file in files:
                #print "ATTN:DEBUG in add_replacement_shadowfiledir_static checking file {0} in dir {1}.".format(file,rootdir)
                new_filepath = os.path.abspath(os.path.join(new_filedirpath+relativedir, file))
                if (os.path.isfile(new_filepath)):
                    orig_filepath = os.path.abspath(os.path.join(rootdir, file))
                    self.add_replacement_filepath(orig_filepath, new_filepath)
            # replace non shadowed subdirs so we dont bother recursing into them?
            subdirscopy = copy.copy(subdirs)
            for subdir in subdirscopy:
                new_filepath = os.path.abspath(os.path.join(new_filedirpath+relativedir, subdir))
                if (not os.path.isdir(new_filepath)):
                    #print "ATTN: skipping recurse of subdir {0} since its not in shadow dir.".format(subdir)
                    subdirs.remove(subdir)




    def replace_filepath(self, filepath):
        """
        When one refers to an asseet file path (such as a view template file), it may be that our configuration settings tell us to use an alternative file.
        For example, a siteaddon may include some default template files (.jn2) files that exist in a subdirectory of the siteaddon module.
        These files may be referred to in code (or in other templates), using a string with an alias, for example: '${addon_account_path}/views/login.jn2'
        This path would be expanded by the asset manager resolve() function, to something like '/testing/mewlo/mpacks/site_addons/account/view/login.jn2'
        But now imagine that a user is creating a custom site and wants to use their own custom login.jn2 replacement template file.
        There are multiple ways this could be done, including subclassing the account siteaddon, but one simple way is to inform the asset manager that
        a replacement file exists for this file.
        This function simply looks up such replacements file paths."""

        #print "ATTN: in replace_filepath with {0}.".format(filepath)

        # first ensure filepath is canonical (replace \ with / and ensure no trailing /)
        filepath = misc.canonicalize_filepath(filepath)
        # now see if its in our static replacement dictionary
        if (filepath in self.replacements_filepaths_static):
            # yes, so return our replacement
            #print "ATTN: found replacementh {0}.".format(self.replacements_filepaths_static[filepath])
            return self.replacements_filepaths_static[filepath]
        # nope, so return it as is
        #print "ATTN: Not found returning as is."
        return filepath

















































    def add_assetmount(self, assetmount):
        """Add a staticfile_mount dictionary, with keys for 'filepath', 'urlpath'."""
        id = assetmount.get_id()
        self.asset_mounts[id] = assetmount

    def add_assetsource(self, assetsource):
        """Add a staticfile_mount dictionary, with keys for 'filepath', 'urlpath'."""
        id = assetsource.get_mnamespacedid()
        self.asset_sources[id] = assetsource





    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "AssetManager (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += self.dumps_description(indent+1)
        outstr += " "*indent + " Aliases:\n"
        for key in sorted(self.aliases):
            outstr += " "*indent + " [{0}] = '{1}'\n".format(key,self.aliases[key])
        outstr += " "*indent + " AssetMounts:\n"
        for (id, assetmount) in self.asset_mounts.iteritems():
            outstr += assetmount.dumps(indent+2)
        outstr += " "*indent + " AssetSources:\n"
        for (id, assetsource) in self.asset_sources.iteritems():
            outstr += assetsource.dumps(indent+2)
        return outstr









    def mountsources(self):
        """Mount our asset sources on our asset mounts."""
        # walk each asset source, choose a real mountpoint for it, then mount it there
        for (id, assetsource) in self.asset_sources.iteritems():
            mountpoint = self.calc_mountpoint_for_assetsource(assetsource)
            mountpoint.mount_source(assetsource, self)

    def calc_mountpoint_for_assetsource(self, assetsource):
        """Calculate which mountpoint this source wants to be mounted at."""
        mountpoint = self.find_mountpoint_byid(assetsource.get_mountid())
        return mountpoint

    def find_mountpoint_byid(self, mountid):
        """Lookup mountpoint by id; return None if not found."""
        if (mountid in self.asset_mounts):
            return self.asset_mounts[mountid]
        return None

    def find_mountsource_byid(self, mountsourceid):
        """Lookup mountpoint by id; return None if not found."""
        if (mountsourceid in self.asset_sources):
            return self.asset_sources[mountsourceid]
        return None



    def get_routegroup_mounting(self):
        """We use a single routegroup under which we create our static routes for internal mount points."""
        if (self.routegroup_mounting == None):
            # create the routegroup
            self.routegroup_mounting = mroute.MewloRouteGroup('assetmanager_routegroup')
            # add routegroup we just created to the site
            self.sitecomp_routemanager().append(self.routegroup_mounting)
        return self.routegroup_mounting


    def shadowfiles(self, filepath_source, filepath_destination, mnamespace, dry_run=0):
        """We want to shadow some (asset) files between directories (recursive into subdirs).
        We may have to create the filepath_target deeply.
        Return failure on error or None."""
        # resolve paths
        filepath_source = self.resolve_filepath(filepath_source, mnamespace)
        filepath_destination = self.resolve_filepath(filepath_destination, mnamespace)
        # now shadow
        # ATTN: this does not support the replacement of files system to let user override specific files, and so needs to be rewritten to support that
        result = misc.copy_tree_withcallback(filepath_source, filepath_destination, dry_run=dry_run, callbackfp = self.shadowcopytree_callback)
        if (dry_run):
            print "ATTN:DEBUG result of shadowfiles from '{0}' to '{1}': {2}".format(filepath_source, filepath_destination,str(result))
        return None


    def shadowcopytree_callback(self, filepath_source, filepath_dest):
        """Return a tuple of the form <BoolShouldCopy, new_filepath_source, new_filepath_dest>."""
        filepath_source = self.resolve_filepath(filepath_source, mnamespace=None)
        return (True, filepath_source, filepath_dest)



    def redirect_asset_aliase_set(self, targetmnamespace, targetid, sourcemnamespace, sourceid):
        """Redirect asset aliases."""
        self.redirect_asset_alias(targetmnamespace, targetid, sourcemnamespace, sourceid, 'urlrel')
        self.redirect_asset_alias(targetmnamespace, targetid, sourcemnamespace, sourceid, 'urlabs')
        self.redirect_asset_alias(targetmnamespace, targetid, sourcemnamespace, sourceid, 'filepath')

    def redirect_asset_alias(self, targetmnamespace, targetid, sourcemnamespace, sourceid, varname):
        """Redirect an asset alias, so one points to the same values as another"""
        sourceval = self.calc_asset_varrep(sourcemnamespace, sourceid, varname)
        targetaliasvarname = self.calc_asset_varname(targetmnamespace, targetid, varname)
        self.add_alias(targetmnamespace, targetaliasvarname, sourceval)


    def calc_source_filepath(self, mountsourceid, subdir=None):
        """Lookup mount source and compute file path to it, with optional subdir."""
        assetsource = self.find_mountsource_byid(mountsourceid)
        filepath = assetsource.get_filepath()
        assetsource_mnamespace = assetsource.get_mnamespace()
        if (subdir):
            filepath += '/'+subdir
        filepath = self.resolve(filepath, assetsource_mnamespace)
        return filepath

    def calc_source_urlpath(self, mountsourceid, subdir=None):
        """Lookup mount source and compute file path to it, with optional subdir."""
        # ATTN:TODO - FIX THIS IS UGLY
        assetsource = self.find_mountsource_byid(mountsourceid)
        urlpathstr = self.calc_asset_varrep(assetsource.get_mnamespace(), assetsource.get_id(), 'urlabs')
        if (subdir):
            urlpathstr += '/'+subdir
        urlpath = self.resolve(urlpathstr, None)
        return urlpath








































class MewloAssetMount(object):
    """Object representing a static asset mount point."""

    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def mount_source(self, assetsource, assetmanager):
        """Mount an asset source on us."""
        # base class does nothing
        pass

    def mount_source_add_aliases(self, assetmanager, assetsource, mnamespace, relurl, absurl, filepath):
        # create and add aliases

        # and now we want to create some aliases for refering to them via url and file
        assetsourceid = assetsource.get_id()
        #
        aliases = {
            assetmanager.calc_asset_varname(mnamespace, assetsourceid, 'urlrel') : relurl,
            assetmanager.calc_asset_varname(mnamespace, assetsourceid, 'urlabs') : absurl,
            assetmanager.calc_asset_varname(mnamespace, assetsourceid, 'filepath') : filepath,
            }
        assetmanager.merge_aliases(mnamespace, aliases)

        # tell source where it's mounted
        assetsource.set_mountpoint(self)




class MewloAssetMount_InternalRoute(MewloAssetMount):
    """Object representing a static asset mount point - handled by internal route."""

    def __init__(self, id, urlpath='assets'):
        """Constructor."""
        super(MewloAssetMount_InternalRoute,self).__init__(id)
        self.urlpath = urlpath

    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "MewloAssetMount_InternalRoute (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += " "*indent + " id={0}\n".format(self.id)
        return outstr


    def mount_source(self, assetsource, assetmanager):
        """Mount an asset source on us.
        For an InternalRoute mount point, this means wiring to a controller that will serve the static assets internally (via mewlo).
        """
        # internal mounts are routed under a special routegroup
        routegroup = assetmanager.get_routegroup_mounting()

        # what should be the path to these files? the source id is guaranteed to be unique so we use that
        mnamespace = assetsource.get_mnamespace()
        routeid = 'assetroute_' + assetsource.get_id()
        routepath = '/{0}/{1}'.format(self.urlpath, assetsource.get_mnamespacedid_forpath())
        filepath = assetsource.get_filepath()

        # create the new route for serving these files at this location
        route = mroute_staticfiles.MewloRoute_StaticFiles(
            id  = routeid,
            path = routepath,
            controller = mcontroller_staticfiles.MewloController_StaticFiles(sourcepath = filepath),
            mnamespace=mnamespace,
        )

        # add the route to our routegroup
        routegroup.append(route)

        # store it in the asset source for later
        assetsource.set_route(route)

        # add aliases
        relurl = assetmanager.resolve_relative_url(routepath, mnamespace=mnamespace)
        absurl = assetmanager.resolve_absolute_url(routepath, mnamespace=mnamespace)
        self.mount_source_add_aliases(assetmanager, assetsource, mnamespace, relurl, absurl, filepath)






class MewloAssetMount_ExternalServer(MewloAssetMount):
    """Object representing a static asset mount point - handled by exposing a directory to an external web server."""

    def __init__(self, id, filepath, urlabs, urlrel=None):
        """Constructor."""
        super(MewloAssetMount_ExternalServer,self).__init__(id)
        self.filepath = filepath
        self.urlabs = urlabs
        if (urlrel == None):
            urlrel = urlabs
        self.urlrel = urlrel

    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "MewloAssetMount_ExternalServer (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += " "*indent + " id={0}, filepath='{1}', urlabs='{2}', urlrel='{2}'\n".format(self.id, self.filepath, self.urlabs, self.urlrel)
        return outstr


    def mount_source(self, assetsource, assetmanager):
        """Mount an asset source on us.
        For an ExternalServer mount point, this means physically copying (shadowing) the contents of the source file directory to a target path, where some other web server will handle serving the files.
        """

        # ok let's shadow the files
        mnamespace = assetsource.get_mnamespace()
        filepath_source = assetsource.get_filepath()
        filepath_destination = self.filepath + '/' + assetsource.get_mnamespacedid_forpath()
        failure = assetmanager.shadowfiles(filepath_source, filepath_destination, mnamespace)

        # for the alias filepath, we could use the source filepath, or the external destination filepath
        # using the former seems easier and more reliable, but using the later might make it easier to spot problems
        # in the future we may want to decide based on what kind of mount and source we are using
        filepath = assetsource.get_filepath()

        # add aliases
        relurl = self.urlrel + '/' + assetsource.get_mnamespacedid_forpath()
        absurl = self.urlabs + '/' + assetsource.get_mnamespacedid_forpath()
        self.mount_source_add_aliases(assetmanager, assetsource, mnamespace, relurl, absurl, filepath)
































class MewloAssetSource(object):
    """Object representing a static asset source directory.
    remember that one should never refer to the assets by a hardcoded url or file path; always use the aliases created by these functions, which will take the form (where ID is the id of the asset source):
    'asset_ID_urlrel' | 'asset_ID_urlabs' | 'asset_ID_filepath'
    """

    def __init__(self, id, mountid, filepath, mnamespace):
        self.id = id
        self.mountid = mountid
        self.filepath = filepath
        self.route = None
        self.mnamespace = mnamespace
        self.mountpoint = None

    def get_id(self):
        return self.id

    def get_mnamespacedid(self):
        """Return mnamespace qualified id."""
        return misc.mnamespacedid(self.mnamespace, self.id)

    def get_mnamespacedid_forpath(self):
        """Return a string with mnamespace incorporated, suitable for use in a file or url path, where a mnamespace separator : would not be an allowed character."""
        return misc.mnamespacedid_forpath(self.mnamespace, self.id)

    def get_mountid(self):
        return self.mountid

    def get_filepath(self):
        return self.filepath

    def get_mnamespace(self):
        return self.mnamespace

    def set_route(self, route):
        self.route = route

    def set_mountpoint(self, mountpoint):
        self.mountpoint = mountpoint

    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "MewloAssetSource ({0}) fullname '{1}' with [mnamespace={2}] reporting in.\n".format(self.__class__.__name__ , self.get_mnamespacedid(), self.mnamespace)
        outstr += " "*indent + " id={0}, mountid={1}, filepath='{2}'\n".format(self.id, self.mountid, self.filepath)
        return outstr




































