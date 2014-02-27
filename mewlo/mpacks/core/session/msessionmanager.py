"""
msessionmanager.py
Helper for database object for storing session data
"""


# mewlo imports
from ..manager import modelmanager
import msession







class MewloSessionManager(modelmanager.MewloModelManager):
    """The MewloSessionManager class helps session management."""


    def __init__(self, mewlosite, debugmode):
        super(MewloSessionManager,self).__init__(mewlosite, debugmode, msession.MewloSession)
        # cookie name
        self.sessionid_cookiename = 'mewlosessionid'

    def startup(self, eventlist):
        super(MewloSessionManager,self).startup(eventlist)

    def shutdown(self):
        super(MewloSessionManager,self).shutdown()


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSessionManager (" + self.__class__.__name__ + ") reporting in.\n"
        outstr += self.dumps_description(indent+1)
        return outstr



    def sitecomp_usermanager(self):
        return self.mewlosite.comp('usermanager')


    def get_sessionid_cookiename(self):
        return self.sessionid_cookiename


    def get_session(self, request, flag_makesessionifnone):
        """Get or create a session data for a request."""
        sessionidinput = request.get_cookieval(self.sessionid_cookiename)
        # now lookup or make new session object (note that sessionid will be None if user does not have cookie set)
        sessionobject = self.lookup_or_make_sessionobject(request, sessionidinput, flag_makesessionifnone)
        return sessionobject




    def lookup_or_make_sessionobject(self, request, sessionidinput, flag_makesessionifnone):
        """Lookup or make new session object (note that sessionid will be None if user does not have cookie set)."""
        if (sessionidinput != None):
            # look it up
            sessionhashkey = self.sanitize_input_sessionid(sessionidinput)
            mewlosession = self.modelclass.find_one_bykey({'hashkey':sessionhashkey})
            if (mewlosession == None):
                # wasn't found, so drop down and make them a new one
                sessionhashkey = None
            else:
                # ok we found it (and loaded it), no need to create it
                # we need to give it reference to us
                mewlosession.set_sessionmanager(self)
                # any fields to set on access?
                if (False):
                    # ATTN: this will cause a SAVE of session db model on EVERY access!!!
                    mewlosession.update_access()
                    # test of serialized session var
                    access_count = mewlosession.get_sessionvar('access_count',0)
                    mewlosession.set_sessionvar('access_count',access_count+1)
                else:
                    access_count = "{0} (but not updated)".format(mewlosession.get_sessionvar('access_count',0))
        else:
            sessionhashkey = None

        if (sessionhashkey == None):
            # no session exists yet
            if (not flag_makesessionifnone):
                # just return saying there is no session
                return None
            # make new one
            mewlosession = self.modelclass()
            # we need to give it reference to us
            mewlosession.set_sessionmanager(self)
            mewlosession.init_values(request.get_remote_addr())
            # get hash key
            sessionhashkey = mewlosession.hashkey
            # test of serialized session var
            access_count = 0
            mewlosession.set_sessionvar('access_count', access_count)
            ## make sure we also send it to client browser via cookie or its useless
            # this is now auto-done by response when saving changed session
            #request.response.set_cookieval(self.sessionid_cookiename, sessionhashkey)

        # debug
        self.mewlosite.logevent('Session hashkey = {0} and access count = {1}.'.format(sessionhashkey,access_count),fields={'accessocount':access_count})
        # return it
        return mewlosession








    def sanitize_input_sessionid(self, sessionid):
        """sessionid is provided by user client, sanitize it or return None on error / bad syntax."""
        #ATTN: TODO - sanitize against regex [0-9A-Za-z_\-]
        return sessionid




