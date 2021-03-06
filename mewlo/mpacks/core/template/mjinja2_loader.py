"""
mninja2_loader.py
Custom loader used to find jinja2 templates.
This is a class that Jinja system uses to help it lookup referenced files; our version lets it find mewlo files.

ATTN: Currently these objects (loader and environment) are created on EACH REQUEST.
If we want to make these classes below not have to be re-created for each request, we need to remove mewlosite variable from init and get it (and or request) dynamically.
"""


import jinja2
import os



class MewloJinja2Loader(jinja2.BaseLoader):
    """Our custom jinja2 template loader is used to load TEMPLATE FILES; it knows how to resolve alias paths."""

    def __init__(self, mewlosite, request):
        super(MewloJinja2Loader,self).__init__()
        self.mewlosite = mewlosite
        self.request = request

    def get_source(self, environment, templatefilepath):
        """Lookup a source template file."""
        mnamespace = self.request.get_matchedroute_mnamespace()
        #print "ATTN: in MewloJinja2Loader get_source() looking for '{0}' in mnamespace '{1}'.".format(templatefilepath, mnamespace)
        path = self.mewlosite.resolve_filepath(templatefilepath, mnamespace)
        if not os.path.exists(path):
            raise jinja2.TemplateNotFound(templatefilepath)
        mtime = os.path.getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        return source, path, lambda: mtime == os.path.getmtime(path)



class MewloJinja2Environment(jinja2.Environment):
    """Our custom jinja2 environment knows how to locate relative paths."""

    def __init__(self, mewlosite, request, loader, undefined):
        super(MewloJinja2Environment, self).__init__(loader=loader, undefined = undefined)
        self.mewlosite = mewlosite

    def join_path(self, templatefilepath, parent):
        """Override join_path() to enable relative template paths."""
        if (templatefilepath.startswith('./')):
            #return os.path.join(os.path.dirname(parent), templatefilepath)
            #return os.path.join(os.path.dirname(parent), templatefilepath[2:])
            return os.path.dirname(parent) + '/' + templatefilepath[2:]
        return templatefilepath





