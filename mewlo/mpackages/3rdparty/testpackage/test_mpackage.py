"""
test_mpackage.py
This file manages a test package
"""


# mewlo imports
from mewlo.mpackages.core.mpackage import MewloPackageObject
from mewlo.mpackages.core.msignals import MewloSignalReceiver
from mewlo.mpackages.core.mregistry import MewloComponent
#
from mewlo.mpackages.core.mglobals import mewlosite


class Test_MewloPackage_Service(object):
    """This is a dummy object that we use to test the component registry.  It pretends to be a service, but it does nothing."""
    def __init__(self):
        pass

    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo Test_MewloPackage_Service reporting in.\n"
        return str




class Test_MewloPackageObject(MewloPackageObject):
    """
    The Test_MewloPackage class defines a test mewlo "package" aka extension/plugin/addon.
    """


    def __init__(self, package):
        # parent constructor
        super(Test_MewloPackageObject, self).__init__(package)




    def startup(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # return failure if any, or None on success


        # ATTN: as a test, let's set up a signal listener for ALL signals
        if (True):
            # create receiver
            callback = self.signalcallback_test
            idfilter = '*'
            sourcefilter = None
            extra = None
            flag_returnsvalue = True
            signalreceiver = MewloSignalReceiver(callback, idfilter, sourcefilter, extra, flag_returnsvalue)
            # now register it with the site dispatcher
            mewlosite().dispatcher.register_receiver(signalreceiver)


        # ATTN: as a test let's add an object to the registry
        if (True):
            # create component
            features = {'name':'test_plugin_service', 'ctype':'m.c.service', 'ptype':'object'}
            # CREATE the object that we are registering (the component registry will hold on to it)
            obj = Test_MewloPackage_Service()
            # now create the component wrapper around it
            component = MewloComponent(features, obj)
            # now register it with the site registry
            mewlosite().registry.register_component(component)

        # lastly, call the parent startup (important!)
        super(Test_MewloPackageObject, self).startup()

        return None




    def signalcallback_test(self, receiverobject, id, message, request, source):
        # we receive a signal callback
        # ATTN: debug test
        msg = "ATTN:DEBUG - From within Test_MewloPackageObject, received a signal callback."
        # log it
        self.log_signalmessage(msg, receiverobject, id, message, request, source)
        # return (result, failure)
        return (None, None)



    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo Test_MewloPackageObject reporting in.\n"
        return str

