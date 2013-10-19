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

    def __init__(self):
        # Invoke parent init and tell it to invoke our local controller_call when triggered
        super(MewloController_StaticFiles,self).__init__(function = self.controller_call)


    def controller_call(self, request, response):
        """The staticfiles controller callable function -- serve a static file."""

        # ok let's build the filepath being requests
        route = request.route
        basefilepath = route.sourcepath
        relpath = '/'.join(request.parsedargs['requestargs'])
        filepath = basefilepath + "/" + relpath
        filepath = request.mewlosite.resolve(filepath)


        # debug info
        #print "----ATTN: Invoking static file controller callable. ----"
        #print "Parsed args: " + str(request.parsedargs)
        #print "Requested file path: " + filepath

        # file exist?
        if (not os.path.isfile(filepath)):
            # file does not exist, respond with error
            request.response.add_status_error(404, "Static file not found or supported on any site: '{0}'.".format(request.get_path()))
            return None

        # file exists, serve it
        response.serve_file_bypath(filepath)
        return None



