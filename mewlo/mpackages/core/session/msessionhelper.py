"""
msessionhelper.py
Database object for storing session data
"""


# mewlo imports
from ..manager import manager
from msession import MewloSession


# python imports
import uuid
import time




class MewloSessionHelper(manager.MewloManager):
    """The MewloSessionHelper class helps session management."""


    def __init__(self):
        super(MewloSessionHelper,self).__init__()
        # cookie name
        self.sessionid_cookiename = 'mewlosessionid'

    def startup(self, mewlosite, eventlist):
        super(MewloSessionHelper,self).startup(mewlosite,eventlist)

    def shutdown(self):
        super(MewloSessionHelper,self).shutdown()


    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        outstr = " "*indent + "MewloSessionHelper (" + self.__class__.__name__ + ") reporting in.\n"
        return outstr






    def get_session(self, request):
        """Get or create a session data for a request."""
        sessionid = request.get_cookieval(self.sessionid_cookiename)
        # now lookup or make new session object (note that sessionid will be None if user does not have cookie set)
        sessionobject = self.lookup_or_make_sessionobject(request, sessionid)
        return sessionobject




    def lookup_or_make_sessionobject(self, request, sessionid):
        """Lookup or make new session object (note that sessionid will be None if user does not have cookie set)."""
        if (sessionid != None):
            # look it up
            # ATTN: TODO - sanitize sessionid
            keydict = {'hashkey':sessionid}
            mewlosession = MewloSession.find_one_bykey(keydict,None)
            if (mewlosession == None):
                # wasn't found, so drop down and make them a new one
                sessionid = None
            else:
                # ok we found it (and loaded it), no need to create it
                # any fields to set on access?
                # test of serialized field
                access_count = mewlosession.get_sessionvar('access_count',0)
                mewlosession.set_sessionvar('access_count',access_count+1)
                #access_count = mewlosession.getfield_serialized('serialized_dict','access_count',0)
                #mewlosession.setfield_serialized('serialized_dict','access_count',access_count+1)
                # save it to our database
                mewlosession.save()

        if (sessionid == None):
            # make new one
            mewlosession = MewloSession()
            # create unique hashid
            sessionid = str(self.create_unique_sessionhashkey())
            mewlosession.hashkey = sessionid
            # other fields to set on creation
            mewlosession.date_create = time.time()
            mewlosession.date_update = mewlosession.date_create
            mewlosession.date_access = mewlosession.date_create
            mewlosession.ip = request.get_remote_addr()
            # test of serialized field
            access_count = 0
            mewlosession.set_sessionvar('access_count', access_count)
            # save it to our database right away?
            mewlosession.save()
            # and for sure save it to response cookie
            request.response.set_cookieval(self.sessionid_cookiename,sessionid)
        # debug
        self.mewlosite.logevent('Session id = {0} and access count = {1}.'.format(sessionid,access_count))
        # return it
        return mewlosession



    def create_unique_sessionhashkey(self):
        """Create a new unique session hashkey."""
        sessionid = uuid.uuid4()
        return sessionid


