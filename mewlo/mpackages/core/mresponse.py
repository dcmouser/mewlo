# mresponse.py
# This file contains classes to support response to requests

# mewlo modules
from helpers.errortracker import ErrorTracker

# this version uses werkzeug to do heavy lifting
from werkzeug.wrappers import Response


class MewloResponse(object):
    """
    The MewloResponse class handles the response to a server request
    """

    def __init__(self, in_request):
        self.request = in_request
        self.isfinalized = False
        #
        self.wresp = None
        #
        self.statuscode = None
        self.headers = None
        self.responsedata = None
        #
        self.errors = ErrorTracker()



    def make_werkzeugresponse(self):
        self.wresp = Response(response = self.responsedata, status = self.statuscode, headers = self.headers)
        return self.wresp



    def start_and_make_wsgiref_response(self, wsgiref_start_response):
        # finalize response, checks any self-consistency stuff
        self.finalize_response()
        # now create werkzeug response via werkzeug
        wresp = self.make_werkzeugresponse()
        # now response to wsgiref from werkzeug is to invoke the callable
        retv = wresp(self.request.get_environ(), wsgiref_start_response)
        # return it
        return retv



    def set_status(self, in_statuscode):
        # set values
        self.statuscode = in_statuscode

    def set_status_ok(self):
        # set values
        self.statuscode = 200

    def add_status_error(self, in_statuscode, in_errorstr):
        # set values
        self.set_status(in_statuscode)
        self.errors.add_errorstr(in_errorstr)

    def set_responsedata(self, in_responsedata, in_statuscode = 200):
        self.responsedata = in_responsedata
        self.statuscode = in_statuscode



    def calc_wsgiref_status_string(self):
        return str(self.statuscode)






    def finalize_response(self):
        # any final error checking?
        if (self.isfinalized):
            return

        # statuscode not set? this is an internal error
        if (self.statuscode == None):
            self.add_status_error(500, "Response statuscode not set")
        # response data not set? this is an internal error
        if (self.responsedata == None):
            self.add_status_error(500, "Response data not set")

        # add errors to response
        self.add_errors_to_response()



    def add_errors_to_response(self):
        if (self.errors.counterrors()==0):
            return
        errorstr = self.errors.tostring()+"."
        if (self.responsedata==None):
            self.responsedata = errorstr
        else:
            self.responsedata.append(errorstr)





    def debug(self, indentstr=""):
        # finalize if its not finalized yet
        self.finalize_response()
        #
        outstr = indentstr+" MewloResponse reporting in.\n"
        outstr += indentstr+"  Status: "+self.calc_wsgiref_status_string()+"\n"
        outstr += indentstr+"  Response Body: "+self.responsedata+"\n"
        return outstr



