"""
test_mpackage.py
This file manages a test package
"""


# mewlo imports
from mewlo.mpackages.core.mpackage import MewloPackageObject
from mewlo.mpackages.core.msignals import MewloSignalReceiver



class Test_MewloPackageObject(MewloPackageObject):
    """
    The Test_MewloPackage class defines a test mewlo "package" aka extension/plugin/addon.
    """


    def __init__(self, package):
        # parent constructor
        super(Test_MewloPackageObject, self).__init__(package)




    def prepare(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # return failure if any, or None on success


        # ATTN: as a test, let's set up a signal listener for ALL signals
        if (True):
            # create receiver
            mewlosite = self.get_mewlosite()
            callback = self.signalcallback_test
            idfilter = '*'
            sourcefilter = None
            extra = None
            flag_returnsvalue = True
            signalreceiver = MewloSignalReceiver(mewlosite, callback, idfilter, sourcefilter, extra, flag_returnsvalue)
            # now hand it off to the site dispatcher
            mewlosite.dispatcher.register_receiver(signalreceiver)

        return None



    def signalcallback_test(self, receiverobject, id, message, source):
        # we receive a signal callback
        # ATTN: debug test
        print "ATTN:DEBUG - From within Test_MewloPackageObject, received a signal callback.  ReceiverObject: "+str(receiverobject)+"; id: "+id+"; message: "+str(message)+"; source: "+str(source)+"\n"
        # return (result, failure)
        return (None, None)





    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo Test_MewloPackageObject reporting in.\n"
        return str

