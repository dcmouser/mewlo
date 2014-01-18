"""
mroute_staticfiles.py
Static file route support
"""


# mewlo imports
import mroute




class MewloRoute_StaticFiles(mroute.MewloRoute):
    """
    The MewloRoute_StaticFiles handles routes to static files
    """


    def __init__(self, id, path, controller, args=[], allow_extra_args=False, extras = None, forcedargs = None):
        super(MewloRoute_StaticFiles,self).__init__(id,path,controller,args=args, allow_extra_args=allow_extra_args, extras=extras, forcedargs=forcedargs)


    def match_args(self, requestargstring):
        """
        For static route, its a match
        """

        argdict = {}
        failure = None

        # remove any trailing '/'
        requestargstringlen = len(requestargstring)
        if (requestargstringlen > 0 and requestargstring[requestargstringlen-1] == '/'):
            requestargstring = requestargstring[:requestargstringlen-1]
        # split argstring into '/' separated words
        if (requestargstring == ''):
            requestargs = []
        else:
            requestargs = requestargstring.split('/')
        requestargcount = len(requestargs)


        # if there were no errors then it's a match, otherwise it's failure to match
        if (failure == None):
            didmatch = True
        else:
            didmatch = False

        #print "HELLO FROM MewloRoute_StaticFiles match = "+str(didmatch)

        argdict['requestargs']=requestargs

        # returnfailf
        return (didmatch, argdict, failure)


