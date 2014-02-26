"""
massetmanager.py
This module contains classes and functions to manage static file assets and aliases.

A MewloSite has a single MewloAssetManager, which it uses to help resolve any references with aliases.
A MewloAssetManager allows aliases to be set, and ensures all references to files and urls are resolved with these aliases.

"""


# mewlo imports
from ..helpers.misc import resolve_expand_string
from ..manager import manager

# python imports





class MewloAssetManager(manager.MewloManager):
    """The derived signal dispatcher."""

    # class constants
    description = "The asset manager handles static files that are served to user"
    typestr = "core"


    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloAssetManager,self).__init__(mewlosite, debugmode)
        self.alias_settings = None

    def startup(self, eventlist):
        super(MewloAssetManager,self).startup(eventlist)

    def shutdown(self):
        super(MewloAssetManager,self).shutdown()



    def set_alias_settings(self, alias_settings):
        """Assign the alias settings."""
        self.alias_settings = alias_settings






    def resolve(self, text):
        """Resolve an alias."""
        if (text==None):
            return None
        if (not isinstance(text, basestring)):
            return text
        resolvedtext = resolve_expand_string(text, self.alias_settings)
        return resolvedtext





    # shortcuts that just call resolve() with some extra info

    def absolute_filepath(self, relpath):
        """Shortcut to resolve a filepath given a relative path."""
        return self.resolve('${sitefilepath}' + relpath)

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
        aliases = {}
        for key,val in self.alias_settings.iteritems():
            aliases[key] = resolve_expand_string(val, self.alias_settings)
        return aliases




