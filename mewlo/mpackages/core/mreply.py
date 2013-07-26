# mreply.py
# This file contains classes to support reply to requests





class MewloReply(object):
    """
    The MewloReply class handles the reply to a server request
    """

    def __init__(self, in_request):
        self.request = in_request
        self.statuscode = 0
        self.statuskeyword = ""
        self.errorstr = ""




    def send_wsgiref_response(self, wsgiref_start_response):
        # finalize reply, checks any self-consistency stuff
        self.finalizereply()
        # status
        status = self.calc_wsgiref_status()
        # headers
        headers = [('Content-Type', 'text/html')]
        # start response before body
        wsgiref_start_response(status, headers)
        # bodies
        bodies = [self.calc_body()]
        return bodies



    def set_status(self, in_statuscode, in_statuskeyword):
        # set values
        self.statuscode = in_statuscode
        self.statuskeyword = in_statuskeyword


    def set_status_ok(self):
        # set values
        self.statuscode = 200
        self.statuskeyword = "OK"


    def set_status_error(self, in_statuscode, in_statuskeyword, in_errorstr):
        # set values
        self.set_status(in_statuscode, in_statuskeyword)
        self.errorstr = in_errorstr





    def calc_wsgiref_status(self):
        return str(self.statuscode)+" "+self.statuskeyword

    def calc_body(self):
        if (self.errorstr==""):
            return "No reply body set."
        return self.errorstr





    def finalizereply(self):
        # any final error checking?
        if (self.statuscode==0):
            # statuscode not set, this is an internal error
            self.set_status_error(500, "Internal Server Error", "Reply was not generated from request.")






    def debug(self, indentstr=""):
        outstr = indentstr+" MewloReply reporting in.\n"
        outstr += indentstr+"  Status: "+self.calc_wsgiref_status()+"\n"
        outstr += indentstr+"  Reply Body: "+self.calc_body()+"\n"
        return outstr



