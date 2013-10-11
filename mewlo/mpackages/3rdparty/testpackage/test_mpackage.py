"""
test_mpackage.py
This file manages a test package
"""


# mewlo imports
import mewlo.mpackages.core.mpackage as mpackage
import mewlo.mpackages.core.msignal as msignal
import mewlo.mpackages.core.mregistry as mregistry
import mewlo.mpackages.core.mglobals as mglobals

# helper imports
from mewlo.mpackages.core.helpers.event.event import EFailure


class Test_MewloPackage_Service(object):
    """This is a dummy object that we use to test the component registry.  It pretends to be a service, but it does nothing."""
    def __init__(self):
        pass

    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo Test_MewloPackage_Service reporting in.\n"
        return str







class Test_MewloPackageObject(mpackage.MewloPackageObject):
    """
    The Test_MewloPackage class defines a test mewlo "package" aka extension/plugin/addon.
    """


    def __init__(self, package):
        # parent constructor
        super(Test_MewloPackageObject, self).__init__(package)


    def startup(self):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # return failure if any, or None on success
        retv = self.setup_everything()
        if (retv != None):
            return retv
        #
        return None



    def shutdown(self):
        # called by Mewlo system when it's ready for us to do any shutdown
        super(Test_MewloPackageObject, self).shutdown()
        return None







    def setup_everything(self):
        # ATTN: as a test, let's set up a signal listener for ALL signals
        if (True):
            # create receiver
            callback = self.signalcallback_test
            idfilter = '*'
            sourcefilter = None
            extra = None
            flag_returnsvalue = True
            signalreceiver = msignal.MewloSignalReceiver(self, callback, idfilter, sourcefilter, extra, flag_returnsvalue)
            # now register it with the site dispatcher
            mglobals.mewlosite().dispatcher.register_receiver(signalreceiver)


        # ATTN: as a test let's add an object to the registry
        if (True):
            # create component
            features = {'ctype':'m.c.service', 'ptype':'object'}
            # CREATE the object that we are registering (the component registry will hold on to it)
            obj = Test_MewloPackage_Service()
            # now create the component wrapper around it
            component = mregistry.MewloComponent('test_plugin_service', self, features, obj)
            # now register it with the site registry
            mglobals.mewlosite().registry.register_component(component)

        # lastly, call the parent startup (important!)
        super(Test_MewloPackageObject, self).startup()

        # success
        return None









    def signalcallback_test(self, receiverobject, id, message, request, source):
        # we receive a signal callback
        # ATTN: debug test
        msg = "ATTN:DEBUG - From within Test_MewloPackageObject, received a signal callback."
        # log it
        self.log_signalmessage(msg, receiverobject, id, message, request, source)
        # return (result, failure)
        return (None, None)








    def checkusable(self):
        """
        See base class for documentation.
        """
        # ATTN: test implementation
        databaseversion = self.get_databaseversion()
        if (databaseversion == None):
            self.log_event("Package 'test_mpackage' reporting that it has not yet been installed.")
        else:
            self.log_event("Package 'test_mpackage' reporting that it's installed database version is: {0}.".format(databaseversion))
        return None
        #return EFailure("The package 'test_mpackage' needs to run a database update before it can run.")

    def generate_update_choices(self):
        """
        Here we want to return a list of update choices to present the user.
        ATTN: TODO - figure out the format of how to return this information.
        """
        return None

    def run_update(self, updatechoice):
        """
        Here we want to run an update.
        ATTN: TODO - figure out the format of the updatechoice stuff.
        :return: None on success, or failure event if not.
        """
        return None





    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo Test_MewloPackageObject reporting in.\n"
        return str

