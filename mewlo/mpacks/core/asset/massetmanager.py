"""
massetmanager.py
This module contains classes and functions to manage static file assets and aliases.

A MewloSite has a single MewloAssetManager, which it uses to help resolve any references with aliases.
A MewloAssetManager allows aliases to be set, and ensures all references to files and urls are resolved with these aliases.

"""


# mewlo imports
from ..helpers import misc
from ..manager import manager

# python imports
import os
import copy





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

    def startup(self, eventlist):
        super(MewloAssetManager,self).startup(eventlist)

    def shutdown(self):
        super(MewloAssetManager,self).shutdown()



    def set_alias_settings(self, alias_settings):
        """Assign the alias settings."""
        self.alias_settings = alias_settings






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






















    def add_replacement_filepath_static(self, orig_filepath, new_filepath):
        """Add a new mapping to replace a filepath."""
        # ATTN: note that we do not handle the case where the new_filepath has been previously rerouted to something else
        # first ensure all are in canonical format
        orig_filepath = self.resolve(misc.canonicalize_filepath(orig_filepath))
        new_filepath = self.resolve(misc.canonicalize_filepath(new_filepath))
        # now add it to our dictionary
        self.replacements_filepaths_static[orig_filepath] = new_filepath
        #print "ATTN:DEBUG adding asset replacement for '{0}' is '{1}'.".format(orig_filepath, new_filepath)


    def add_replacement_mirrorfiledir_static(self, orig_filedirpath, new_filedirpath):
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
                    self.add_replacement_filepath_static(orig_filepath, new_filepath)
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


