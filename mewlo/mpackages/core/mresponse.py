"""
mresponse.py
This file contains classes to support response to requests
"""




# mewlo modules
from helpers.eventtracker import EventTracker

# this version uses werkzeug to do heavy lifting
from werkzeug.wrappers import Response





class MewloResponse(object):
    """
    The MewloResponse class handles the response to a server request
    """

    def __init__(self, request):
        self.request = request
        self.isfinalized = False
        #
        self.wresp = None
        #
        self.statuscode = None
        self.headers = None
        self.responsedata = None
        #
        self.errors = EventTracker()



    def make_werkzeugresponse(self):
        """Create a werkzeug response object and attach it to us."""
        self.wresp = Response(response = self.responsedata, status = self.statuscode, headers = self.headers)
        return self.wresp



    def start_and_make_wsgiref_response(self, wsgiref_start_response):
        """This is invoked when we want to send a final response to the wsgi web server."""

        # finalize response, checks any self-consistency stuff
        self.finalize_response()
        # now create werkzeug response via werkzeug
        wresp = self.make_werkzeugresponse()
        # now response to wsgiref from werkzeug is to invoke the callable
        retv = wresp(self.request.get_environ(), wsgiref_start_response)
        # return it
        return retv



    def set_status(self, statuscode):
        # set values
        self.statuscode = statuscode

    def set_status_ok(self):
        # set values
        self.statuscode = 200

    def add_status_error(self, statuscode, errorstr):
        # set values
        self.set_status(statuscode)
        self.errors.error(errorstr)

    def set_responsedata(self, responsedata, statuscode = 200):
        self.responsedata = responsedata
        self.statuscode = statuscode

    def calc_wsgiref_status_string(self):
        return str(self.statuscode)






    def finalize_response(self):
        """
        This function is invoked after the response is finished being built and is about to be sent as a reply.
        It is responsible for final error checking, and will do things like display an error if no response has been set.
        """

        # any final error checking?
        if (self.isfinalized):
            return
        self.isfinalized = True

        # statuscode not set? this is an internal error
        if (self.statuscode == None):
            self.add_status_error(500, u"Response statuscode not set")
        # response data not set? this is an internal error
        if (self.responsedata == None):
            self.add_status_error(500, u"Response data not set")

        # add errors to response
        self.add_errors_to_response()




    def add_errors_to_response(self):
        """Helper funciton to add any pending accumulated errors to the response."""

        if (self.errors.count_errors()==0):
            return
        errorstr = self.errors.tostring()+"."
        if (self.responsedata==None):
            self.responsedata = errorstr
        else:
            self.responsedata.append(errorstr)





    def debug(self, indentstr=""):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        # finalize if its not finalized yet
        self.finalize_response()
        #
        outstr = indentstr+" MewloResponse reporting in.\n"
        outstr += indentstr+"  Status: "+self.calc_wsgiref_status_string()+"\n"
        outstr += indentstr+"  Response Body: "+self.responsedata+"\n"
        return outstr



