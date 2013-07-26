# mresponse.py
# This file contains classes to support response to requests


# this version uses werkzeug to do heavy lifting
from werkzeug.wrappers import Response


class MewloResponse(object):
    """
    The MewloResponse class handles the response to a server request
    """

    def __init__(self, in_request):
        self.request = in_request
        self.wresp = None
        self.statuscode = 0
        self.statuskeyword = ""
        self.errorstr = ""



    def make_werkzeugrequest(self, responsedata):
        self.wresp = Response(responsedata, self.statuscode)
        return self.wresp



    def start_and_make_wsgiref_response(self, wsgiref_start_response):
        # finalize response, checks any self-consistency stuff
        self.finalize_response()
        # get response data
        responsedata = self.calc_body()
        # now create werkzeug response via werkzeug
        wresp = self.make_werkzeugrequest(responsedata)
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


    def set_status_error(self, in_statuscode, in_errorstr):
        # set values
        self.set_status(in_statuscode)
        self.errorstr = in_errorstr





    def calc_wsgiref_status(self):
        return str(self.statuscode)

    def calc_body(self):
        if (self.errorstr==""):
            return "No response body set."
        return self.errorstr





    def finalize_response(self):
        # any final error checking?
        if (self.statuscode==0):
            # statuscode not set, this is an internal error
            self.set_status_error(500, "Response was not generated from request.")






    def debug(self, indentstr=""):
        outstr = indentstr+" MewloResponse reporting in.\n"
        outstr += indentstr+"  Status: "+self.calc_wsgiref_status()+"\n"
        outstr += indentstr+"  Response Body: "+self.calc_body()+"\n"
        return outstr



