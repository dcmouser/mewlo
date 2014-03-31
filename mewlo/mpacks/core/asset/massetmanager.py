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


    def merge_aliases(self, aliases, namespace):
        """Merge in some aliases."""
        for (key,val) in aliases.iteritems():
            self.add_alias(key, val, namespace)

    def add_alias(self, aliasname, aliasval, namespace):
        """Add an alias."""
        hashkey = misc.namespacedid(namespace, aliasname)
        self.aliases[hashkey] = aliasval














































    def get_raw_aliasval(self, varname, namespace):
        """Resolve string that could include $ aliases, without replacing/expanding."""
        text = misc.lookup_namespaced_byid(varname, namespace, self.aliases)
        print "ATTN: found '{0}' with var {1} ns={2} in '{3}'.".format(str(text),varname,namespace,str(self.aliases))
        return text




    def resolve(self, text, namespace):
        """Resolve a string that could include $ aliases.  This is the central function that many places call."""
        if (text==None):
            return None
        if (not isinstance(text, basestring)):
            return text
        # ok resolve aliases -- for now we use a helper function to do the main work
        resolvedtext = misc.resolve_expand_string(text, self.aliases, namespace)
        # now we have a fully resolved string that may have contained some aliases
        return resolvedtext





    def resolve_filepath(self, text, namespace):
        """Call resolve THEN call replace_filepath."""
        resolvedtext = self.resolve(text, namespace)
        resolvedtext = self.replace_filepath(resolvedtext)
        #print "ATTN:DEBUG resolved '{0}' to '{1}'.".format(text, resolvedtext)
        return resolvedtext


    def resolve_filepath_canonical_noreplace(self, text, namespace):
        """Resolve string that could include $ aliases, AND THEN canonicalize it."""
        text = self.resolve(text, namespace)
        text = misc.canonicalize_filepath(text)
        return text





    # shortcuts that just call resolve() with some extra info

    def resolve_absolute_filepath(self, relpath, namespace):
        """Shortcut to resolve a filepath given a relative path."""
        return self.resolve_filepath('${sitefilepath}' + relpath, namespace)

    def resolve_absolute_url(self, relpath, namespace):
        """Shortcut to resolve a url given a relative path."""
        if (misc.isabsoluteurl(relpath)):
            return self.resolve(relpath, namespace)
        return self.resolve('${siteurl_absolute}' + relpath, namespace)

    def resolve_relative_url(self, relpath, namespace):
        """Shortcut to resolve a url that is relative to our server root."""
        if (misc.isabsoluteurl(relpath)):
            return self.resolve(relpath, namespace)
        return self.resolve('${siteurl_relative}' + relpath, namespace)





    def get_resolvedaliases_UNUSED(self, namespace):
        """Return a dictionary of resolved aliases; might be useful for templates."""
        # ATTN: Note that most aliases will not need resolving, but some may recurively include each other, that's why we have to do this
        # ATTN: Note that this could be quite slow unless we do it smartly -- would be nice to cache this result so that we don't have to recreate it each call
        # ATTN: TODO eliminate this function
        aliases = {}
        for key,val in self.aliases.iteritems():
            aliases[key] = misc.resolve_expand_string(val, self.aliases, namespace)
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
        filepath = self.resolve_filepath_canonical_noreplace(filepath, namespace=None)
        potentialparent_filepath = self.resolve_filepath_canonical_noreplace(potentialparent_filepath, namespace=None)
        if (filepath.startswith(potentialparent_filepath)):
            return True
        return False



    def add_replacement_filepath(self, orig_filepath, new_filepath):
        """Add a new mapping to replace a filepath."""
        # ATTN: note that we do not handle the case where the new_filepath has been previously rerouted to something else
        # first ensure all are in canonical format
        orig_filepath = self.resolve_filepath_canonical_noreplace(orig_filepath, namespace=None)
        new_filepath = self.resolve_filepath_canonical_noreplace(new_filepath, namespace=None)
        # now add it to our dictionary
        self.replacements_filepaths_static[orig_filepath] = new_filepath
        #print "ATTN:DEBUG adding asset replacement for '{0}' is '{1}'.".format(orig_filepath, new_filepath)


    def add_replacement_shadowfiledir(self, orig_filedirpath, new_filedirpath, flag_mkpath_root):
        """Traverse two shadow didrectories and add cases where there exists replacement files in the new filedirpath."""
        # first ensure all are in canonical format
        #print "ATTN: walking in add_replacement_shadowfiledir_static1 for '{0}' with filepath1 '{1}'.".format(orig_filedirpath, new_filedirpath)
        orig_filedirpath = self.resolve_filepath_canonical_noreplace(orig_filedirpath, namespace=None)
        new_filedirpath = self.resolve_filepath_canonical_noreplace(new_filedirpath, namespace=None)
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
        id = assetsource.get_namespacedid()
        self.asset_sources[id] = assetsource





    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "AssetManager (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += self.dumps_description(indent+1)
        outstr += " "*indent + " Aliases:\n"
        for (key, val) in self.aliases.iteritems():
            outstr += " "*indent + " [{0}] = '{1}'\n".format(key,val)
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
            self.routegroup_mounting = mroute.MewloRouteGroup()
            # add routegroup we just created to the site
            self.sitecomp_routemanager().append(self.routegroup_mounting)
        return self.routegroup_mounting


    def shadowfiles(self, filepath_source, filepath_destination, namespace, dry_run=0):
        """We want to shadow some (asset) files between directories (recursive into subdirs).
        We may have to create the filepath_target deeply.
        Return failure on error or None."""
        # resolve paths
        filepath_source = self.resolve_filepath(filepath_source, namespace)
        filepath_destination = self.resolve_filepath(filepath_destination, namespace)
        # now shadow
        # ATTN: this does not support the replacement of files system to let user override specific files, and so needs to be rewritten to support that
        result = misc.copy_tree_withcallback(filepath_source, filepath_destination, dry_run=dry_run, callbackfp = self.shadowcopytree_callback)
        if (dry_run):
            print "ATTN:DEBUG result of shadowfiles from '{0}' to '{1}': {2}".format(filepath_source, filepath_destination,str(result))
        return None


    def shadowcopytree_callback(self, filepath_source, filepath_dest):
        """Return a tuple of the form <BoolShouldCopy, new_filepath_source, new_filepath_dest>."""
        filepath_source = self.resolve_filepath(filepath_source, namespace=None)
        return (True, filepath_source, filepath_dest)



    def redirect_asset_aliases(self, targetnamespace, targetid, sourcenamespace, sourceid):
        """Redirect asset aliases."""
        self.redirect_asset_alias(targetnamespace, targetid, sourcenamespace, sourceid, '_urlrel')
        self.redirect_asset_alias(targetnamespace, targetid, sourcenamespace, sourceid, '_urlabs')
        self.redirect_asset_alias(targetnamespace, targetid, sourcenamespace, sourceid, '_filepath')

    def redirect_asset_alias(self, targetnamespace, targetid, sourcenamespace, sourceid, suffixstr):
        """Redirect an asset alias, so one points to the same values as another"""
        sourcealiasstr = 'asset_' + sourceid + suffixstr
        targetaliasstr = 'asset_' + targetid + suffixstr
        sourceval = '${' + misc.namespacedid(sourcenamespace, sourcealiasstr) + '}'
        self.add_alias(targetaliasstr, sourceval, targetnamespace)


    def calc_source_filepath(self, mountsourceid, subdir=None):
        """Lookup mount source and compute file path to it, with optional subdir."""
        assetsource = self.find_mountsource_byid(mountsourceid)
        filepath = assetsource.get_filepath()
        assetsource_namespace = assetsource.get_namespace()
        if (subdir):
            filepath += '/'+subdir
        filepath = self.resolve(filepath, assetsource_namespace)
        return filepath

    def calc_source_urlpath(self, mountsourceid, subdir=None):
        """Lookup mount source and compute file path to it, with optional subdir."""
        # ATTN:TODO - FIX THIS IS UGLY
        assetsource = self.find_mountsource_byid(mountsourceid)
        urlpath = '${asset_'+assetsource.get_id()+'_urlabs}'
        assetsource_namespace = assetsource.get_namespace()
        if (subdir):
            urlpath += '/'+subdir
        urlpath = self.resolve(urlpath, assetsource_namespace)
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
        namespace = assetsource.get_namespace()
        routeid = 'assetroute_' + assetsource.get_id()
        routepath = '/{0}/{1}'.format(self.urlpath, assetsource.get_namespacedidpath())
        filepath = assetsource.get_filepath()

        # create the new route for serving these files at this location
        route = mroute_staticfiles.MewloRoute_StaticFiles(
            id  = routeid,
            path = routepath,
            controller = mcontroller_staticfiles.MewloController_StaticFiles(sourcepath = filepath),
            namespace=namespace,
        )

        # add the route to our routegroup
        routegroup.append(route)

        # store it in the asset source for later
        assetsource.set_route(route)

        # and now we want to create some aliases for refering to them via url and file
        aliasprefix = 'asset_' + assetsource.get_id()
        aliases = {
            aliasprefix + '_urlrel' : assetmanager.resolve_relative_url(routepath, namespace=namespace),
            aliasprefix + '_urlabs' : assetmanager.resolve_absolute_url(routepath, namespace=namespace),
            aliasprefix + '_filepath' : filepath,
            }
        assetmanager.merge_aliases(aliases, namespace)

        # tell source where it's mounted
        assetsource.set_mountpoint(self)




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
        namespace = assetsource.get_namespace()
        filepath_source = assetsource.get_filepath()
        filepath_destination = self.filepath + '/' + assetsource.get_namespacedidpath()
        failure = assetmanager.shadowfiles(filepath_source, filepath_destination, namespace)

        # for the alias filepath, we could use the source filepath, or the external destination filepath
        # using the former seems easier and more reliable, but using the later might make it easier to spot problems
        # in the future we may want to decide based on what kind of mount and source we are using
        aliasfilepath = assetsource.get_filepath()

        # and now we want to create some aliases for refering to them via url and file
        aliasprefix = 'asset_' + assetsource.get_id()
        aliases = {
            aliasprefix + '_urlrel' : self.urlrel + '/' + assetsource.get_namespacedidpath(),
            aliasprefix + '_urlabs' : self.urlabs + '/' + assetsource.get_namespacedidpath(),
            aliasprefix + '_filepath' : aliasfilepath,
            }
        assetmanager.merge_aliases(aliases, namespace)

        # tell source where it's mounted
        assetsource.set_mountpoint(self)































class MewloAssetSource(object):
    """Object representing a static asset source directory.
    remember that one should never refer to the assets by a hardcoded url or file path; always use the aliases created by these functions, which will take the form (where ID is the id of the asset source):
    'asset_ID_urlrel' | 'asset_ID_urlabs' | 'asset_ID_filepath'
    """

    def __init__(self, id, mountid, filepath, namespace):
        self.id = id
        self.mountid = mountid
        self.filepath = filepath
        self.route = None
        self.namespace = namespace
        self.mountpoint = None

    def get_id(self):
        return self.id

    def get_namespacedid(self):
        if (self.namespace):
            return self.namespace+'::'+self.id
        return self.id

    def get_namespacedidpath(self):
        if (self.namespace):
            return self.namespace+'_'+self.id
        return self.id

    def get_mountid(self):
        return self.mountid

    def get_filepath(self):
        return self.filepath

    def get_namespace(self):
        return self.namespace

    def set_route(self, route):
        self.route = route

    def set_mountpoint(self, mountpoint):
        self.mountpoint = mountpoint

    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "MewloAssetSource ({0}) [namespace={1}] reporting in.\n".format(self.__class__.__name__ , self.namespace)
        outstr += " "*indent + " id={0}, mountid={1}, filepath='{2}'\n".format(self.id, self.mountid, self.filepath)
        return outstr




































