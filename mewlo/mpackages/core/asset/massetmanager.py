"""
massetmanager.py
This module contains classes and functions to manage static file assets and aliases.

The asset manager has several functions:

    * It allows aliases to be set, and ensures all references to files and urls are resolved with these aliases.


"""


# mewlo imports
from ..helpers.misc import resolve_expand_string

# python imports





class MewloAssetManager(object):
    """The derived signal dispatcher."""

    def __init__(self):
        """Constructor."""
        self.alias_settings = None

    def startup(self, mewlosite, eventlist):
        self.mewlosite = mewlosite

    def shutdown(self):
        pass



    def set_alias_settings(self, alias_settings):
        """Assign the alias settings."""
        self.alias_settings = alias_settings






    def resolve(self, text):
        """Resolve an alias."""
        resolvedtext = resolve_expand_string(text, self.alias_settings)
        return resolvedtext





    # shortcuts that just call resolve() with some extra info

    def absolute_filepath(self, relpath):
        """Shortcut to resolve a filepath given a relative path."""
        return self.resolve('${sitefilepath}' + relpath)

    def absolute_url(self, relpath):
        """Shortcut to resolve a url given a relative path."""
        return self.resolve('${siteurl_absolute}' + relpath)

    def relative_url(self, relpath):
        """Shortcut to resolve a url that is relative to our server root."""
        return self.resolve('${siteurl_relative}' + relpath)






    def get_resolvedaliases(self):
        """Return a dictionary of resolved aliases; might be useful for templates."""
        # ATTN: Note that most aliases will not need resolving, but some may recurively include each other, that's why we have to do this
        # ATTN: Note that this could be quite slow unless we do it smartly -- would be nice to cache this result so that we don't have to recreate it each call
        aliases = {}
        for aliaskey in self.alias_settings.keys():
            aliases[aliaskey] = resolve_expand_string(self.alias_settings[aliaskey], self.alias_settings)
        return aliases
