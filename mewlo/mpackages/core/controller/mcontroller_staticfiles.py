"""
mcontroller_staticfiles.py
Controller made to serve static files.
"""


# mewlo imports
import mcontroller

# python imports
import os





class MewloController_StaticFiles(mcontroller.MewloController):
    """
    The MewloController_StaticFiles class handles requests for static files
    """

    def __init__(self, sourcepath):
        # Invoke parent init and tell it to invoke our local controller_call when triggered
        super(MewloController_StaticFiles,self).__init__(function = self.controller_call)
        self.sourcepath = sourcepath


    def controller_call(self, request, response):
        """The staticfiles controller callable function -- serve a static file."""

        # ok let's build the filepath being requests
        route = request.route
        basefilepath = self.sourcepath
        relpath = '/'.join(request.parsedargs['requestargs'])
        filepath = basefilepath + "/" + relpath
        filepath = request.mewlosite.resolve(filepath)

        # ATTN: TODO -- make sure user is not trying any .. tricks to get us to back up past source direcotry
        # ATTN: TODO -- does our call to request.mewlosite.resolve create a danger of them using alias paths to get at our files?

        # file exist?
        if (not os.path.isfile(filepath)):
            # file does not exist, respond with error
            request.response.add_status_error(404, "Static file not found or supported on any site: '{0}'.".format(request.get_path()))
            return None

        # file exists, serve it
        response.serve_file_bypath(filepath)
        return None



