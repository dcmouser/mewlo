"""
mrequesthelper.py
"""


# mewlo imports









class MewloRequestHandlerHelper(object):
    """Base class for different request handling helpers. For example see accountmanager"""

    def __init__(self, request, response):
        self.request = request
        self.response = response





    def get_mewlosite(self):
        return self.request.mewlosite

    def sitecomp_usermanager(self):
        return self.request.mewlosite.comp('usermanager')

    def sitecomp_verificationmanager(self):
        return self.request.mewlosite.comp('verificationmanager')

    def sitecomp_mailmanager(self):
        return self.request.mewlosite.comp('mailmanager')






    def set_renderpageid(self, pageid):
        """Helper function to set page id."""
        self.response.set_renderpageid(pageid)


    def calc_localtemplatepath(self, viewfilepath):
        return self.viewbasepath+viewfilepath

    def render_localview(self, viewfilepath, args=None):
        """Helper function to render relative view file."""
        self.response.render_from_template_file(self.calc_localtemplatepath(viewfilepath), args=args)