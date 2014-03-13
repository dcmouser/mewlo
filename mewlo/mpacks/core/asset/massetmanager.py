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
        self.alias_settings = None
        self.replacements_filepaths_static = {}
        self.asset_mounts = {}
        self.asset_sources = {}
        self.routegroup_mounting = None

    def prestartup_register(self, eventlist):
        super(MewloAssetManager,self).prestartup_register(eventlist)
        # we mount our sources here at this stage, BEFORE startup() because at the point it will be too late to add new routes
        self.mountsources()


    def startup(self, eventlist):
        super(MewloAssetManager,self).startup(eventlist)

    def shutdown(self):
        super(MewloAssetManager,self).shutdown()



    def set_alias_settings(self, alias_settings):
        """Assign the alias settings."""
        self.alias_settings = alias_settings


    def add_alias(self, aliasname, aliasval):
        """Add an alias."""
        self.alias_settings[aliasname] = aliasval



    def resolve(self, text):
        """Resolve a string that could include $ aliases.  This is the central function that many places call."""
        if (text==None):
            return None
        if (not isinstance(text, basestring)):
            return text
        # ok resolve aliases -- for now we use a helper function to do the main work
        resolvedtext = misc.resolve_expand_string(text, self.alias_settings)
        # now we have a fully resolved string that may have contained some aliases
        return resolvedtext





    def resolve_filepath(self, text):
        """Call resolve THEN call replace_filepath."""
        resolvedtext = self.resolve(text)
        resolvedtext = self.replace_filepath(resolvedtext)
        return resolvedtext








    # shortcuts that just call resolve() with some extra info

    def absolute_filepath(self, relpath):
        """Shortcut to resolve a filepath given a relative path."""
        return self.resolve_filepath('${sitefilepath}' + relpath)

    def absolute_url(self, relpath):
        """Shortcut to resolve a url given a relative path."""
        if (self.isabsoluteurl(relpath)):
            return relpath
        return self.resolve('${siteurl_absolute}' + relpath)

    def relative_url(self, relpath):
        """Shortcut to resolve a url that is relative to our server root."""
        if (self.isabsoluteurl(relpath)):
            return relpath
        return self.resolve('${siteurl_relative}' + relpath)

    def isabsoluteurl(self, urlpath):
        """Return True if urlpath is already an absolute path (starting with http)."""
        if (urlpath.startswith('http')):
            return True
        return False



    def get_resolvedaliases(self):
        """Return a dictionary of resolved aliases; might be useful for templates."""
        # ATTN: Note that most aliases will not need resolving, but some may recurively include each other, that's why we have to do this
        # ATTN: Note that this could be quite slow unless we do it smartly -- would be nice to cache this result so that we don't have to recreate it each call
        # ATTN: TODO eliminate this function
        aliases = {}
        for key,val in self.alias_settings.iteritems():
            aliases[key] = misc.resolve_expand_string(val, self.alias_settings)
        return aliases






















    def add_replacement_filepath(self, orig_filepath, new_filepath):
        """Add a new mapping to replace a filepath."""
        # ATTN: note that we do not handle the case where the new_filepath has been previously rerouted to something else
        # first ensure all are in canonical format
        orig_filepath = self.resolve(misc.canonicalize_filepath(orig_filepath))
        new_filepath = self.resolve(misc.canonicalize_filepath(new_filepath))
        # now add it to our dictionary
        self.replacements_filepaths_static[orig_filepath] = new_filepath
        #print "ATTN:DEBUG adding asset replacement for '{0}' is '{1}'.".format(orig_filepath, new_filepath)


    def add_replacement_mirrorfiledir(self, orig_filedirpath, new_filedirpath):
        """Traverse two mirror didrectories and add cases where there exists replacement files in the new filedirpath."""
        # first ensure all are in canonical format
        #print "ATTN: walking in add_replacement_mirrorfiledir_static with filepath1 '{0}'.".format(orig_filedirpath)
        orig_filedirpath = self.resolve(misc.canonicalize_filepath(orig_filedirpath))
        new_filedirpath = self.resolve(misc.canonicalize_filepath(new_filedirpath))
        orig_filedirpath_len = len(orig_filedirpath)
        #print "ATTN: walking in add_replacement_mirrorfiledir_static with filepath '{0}'.".format(orig_filedirpath)
        # now recurse deep in orig_filepath
        for (rootdir, subdirs, files) in os.walk(orig_filedirpath):
            # ok we have a candidate rootdir -- we want to get the relative path from orig_filedirpath
            if (rootdir.startswith(orig_filedirpath)):
                # remove it
                relativedir = rootdir[orig_filedirpath_len:]
            else:
                # error
                raise Exception("Walking directory '{0}' in add_replacement_mirrorfiledir_static and unexpectedly got a dir that doesn't start with base directory; but instead is: '{1}'.".format(orig_filedirpath,rootdir))
            for file in files:
                #print "ATTN:DEBUG in add_replacement_mirrorfiledir_static checking file {0} in dir {1}.".format(file,rootdir)
                new_filepath = os.path.abspath(os.path.join(new_filedirpath+relativedir, file))
                if (os.path.isfile(new_filepath)):
                    orig_filepath = os.path.abspath(os.path.join(rootdir, file))
                    self.add_replacement_filepath(orig_filepath, new_filepath)
            # replace non mirrored subdirs so we dont bother recursing into them?
            subdirscopy = copy.copy(subdirs)
            for subdir in subdirscopy:
                new_filepath = os.path.abspath(os.path.join(new_filedirpath+relativedir, subdir))
                if (not os.path.isdir(new_filepath)):
                    #print "ATTN: skipping recurse of subdir {0} since its not in mirror dir.".format(subdir)
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
        id = assetsource.get_id()
        self.asset_sources[id] = assetsource





    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "AssetManager (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += self.dumps_description(indent+1)
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

    def get_routegroup_mounting(self):
        """We use a single routegroup under which we create our static routes for internal mount points."""
        if (self.routegroup_mounting == None):
            # create the routegroup
            self.routegroup_mounting = mroute.MewloRouteGroup()
            # add routegroup we just created to the site
            self.sitecomp_routemanager().append(self.routegroup_mounting)
        return self.routegroup_mounting


    def mirrorfiles(self, filepath_source, filepath_destination, dry_run=0):
        """We want to mirror some (asset) files between directories (recursive into subdirs).
        We may have to create the filepath_target deeply.
        Return failure on error or None."""
        # resolve paths
        filepath_source = self.resolve_filepath(filepath_source)
        filepath_destination = self.resolve_filepath(filepath_destination)
        # now mirror
        result = distutils.dir_util.copy_tree(filepath_source, filepath_destination, dry_run=dry_run)
        if (dry_run):
            print "ATTN:DEBUG result of mirrorfiles from '{0}' to '{1}': {2}".format(filepath_source, filepath_destination,str(result))
        return None































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
        routeid = 'assetroute_' + assetsource.get_id()
        routepath = '/{0}/{1}'.format(self.urlpath, assetsource.get_id())
        filepath = assetsource.get_filepath()

        # create the new route for serving these files at this location
        route = mroute_staticfiles.MewloRoute_StaticFiles(
            id  = routeid,
            path = routepath,
            controller = mcontroller_staticfiles.MewloController_StaticFiles(sourcepath = filepath),
        )

        # add the route to our routegroup
        routegroup.append(route)

        # store it in the asset source for later
        assetsource.set_route(route)

        # and now we want to create some aliases for refering to them via url and file
        aliasprefix = 'asset_' + assetsource.get_id()
        assetmanager.add_alias(aliasprefix + '_urlrel', assetmanager.mewlosite.relative_url(routepath))
        assetmanager.add_alias(aliasprefix + '_urlabs', assetmanager.mewlosite.absolute_url(routepath))
        assetmanager.add_alias(aliasprefix + '_filepath', filepath)





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
        For an ExternalServer mount point, this means physically copying (mirroring) the contents of the source file directory to a target path, where some other web server will handle serving the files.
        """

        # ok let's mirror the files
        filepath_source = assetsource.get_filepath()
        filepath_destination = self.filepath + '/' + assetsource.get_id()
        failure = assetmanager.mirrorfiles(filepath_source, filepath_destination)

        # for the alias filepath, we could use the source filepath, or the external destination filepath
        # using the former seems easier and more reliable, but using the later might make it easier to spot problems
        # in the future we may want to decide based on what kind of mount and source we are using
        aliasfilepath = assetsource.get_filepath()

        # and now we want to create some aliases for refering to them via url and file
        aliasprefix = 'asset_' + assetsource.get_id()
        assetmanager.add_alias(aliasprefix + '_urlrel', self.urlrel + '/' + assetsource.get_id())
        assetmanager.add_alias(aliasprefix + '_urlabs', self.urlabs + '/' + assetsource.get_id())
        assetmanager.add_alias(aliasprefix + '_filepath', aliasfilepath)


































class MewloAssetSource(object):
    """Object representing a static asset source directory.
    remember that one should never refer to the assets by a hardcoded url or file path; always use the aliases created by these functions, which will take the form (where ID is the id of the asset source):
    'asset_ID_urlrel' | 'asset_ID_urlabs' | 'asset_ID_filepath'
    """

    def __init__(self, id, mountid, filepath):
        self.id = id
        self.mountid = mountid
        self.filepath = filepath
        self.route = None

    def get_id(self):
        return self.id

    def get_mountid(self):
        return self.mountid

    def get_filepath(self):
        return self.filepath

    def set_route(self, route):
        self.route = route

    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "MewloAssetSource (" + self.__class__.__name__  + ") reporting in.\n"
        outstr += " "*indent + " id={0}, mountid={1}, filepath='{2}'\n".format(self.id, self.mountid, self.filepath)
        return outstr




































