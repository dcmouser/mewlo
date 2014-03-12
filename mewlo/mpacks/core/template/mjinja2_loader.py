"""
mninja2_loader.py
Custom loader used to find jinja2 templates.
This is a class that Jinja system uses to help it lookup referenced files; our version lets it find mewlo files.
"""


import jinja2
import os



class MewloJinja2Loader(jinja2.BaseLoader):
    """Our custom jinja2 template loader is used to load TEMPLATE FILES; it knows how to resolve alias paths."""

    def __init__(self, mewlosite):
        super(MewloJinja2Loader,self).__init__()
        self.mewlosite = mewlosite

    def get_source(self, environment, template):
        path = self.mewlosite.resolve_filepath(template)
        if not os.path.exists(path):
            raise jinja2.TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        return source, path, lambda: mtime == os.path.getmtime(path)



class MewloJinja2Environment(jinja2.Environment):
    """Our custom jinja2 environment knows how to locate relative paths."""

    def __init__(self, mewlosite, loader, undefined):
        super(MewloJinja2Environment,self).__init__(loader=loader, undefined = undefined)
        self.mewlosite = mewlosite

    def join_path(self, template, parent):
        """Override join_path() to enable relative template paths."""
        if (template.startswith('./')):
            return os.path.join(os.path.dirname(parent), template)
        return template





