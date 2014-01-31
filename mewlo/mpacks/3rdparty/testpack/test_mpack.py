"""
test_mpack.py
This file manages a test pack
"""


# mewlo imports
from mewlo.mpacks.core.pack import mpackobject
from mewlo.mpacks.core.signal import msignal
from mewlo.mpacks.core.registry import mregistry

# helper imports
from mewlo.mpacks.core.eventlog.mevent import EFailure, EWarning

# python imports
import datetime




class Test_MewloPack_Service(object):
    """This is a dummy object that we use to test the component registry.  It pretends to be a service, but it does nothing."""
    def __init__(self):
        pass

    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo Test_MewloPack_Service reporting in.\n"
        return str







class Test_MewloPackObject(mpackobject.MewloPackObject):
    """
    The Test_MewloPack class defines a test mewlo "pack" aka extension/plugin/addon.
    """


    def __init__(self, pack):
        # parent constructor
        super(Test_MewloPackObject, self).__init__(pack)


    def startup(self, mewlosite, eventlist):
        # called by Mewlo system when it's ready for us to do any setup stuff
        # return failure if any, or None on success
        retv = self.setup_everything(mewlosite, eventlist)
        if (retv != None):
            return retv
        #
        return None



    def shutdown(self):
        # called by Mewlo system when it's ready for us to do any shutdown
        super(Test_MewloPackObject, self).shutdown()
        return None







    def setup_everything(self, mewlosite, eventlist):
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
            mewlosite.comp('signalmanager').register_receiver(signalreceiver)


        # ATTN: as a test let's add an object to the registry
        if (True):
            # create component
            features = {'type':'custom', 'ptype':'object'}
            # CREATE the object that we are registering (the component registry will hold on to it)
            obj = Test_MewloPack_Service()
            # now create the component wrapper around it
            component = mregistry.MewloComponent('test_plugin_service', self, features, obj)
            # now register it with the site registry
            mewlosite.comp('registrymanager').register_component(component)

        # lastly, call the parent startup (important!)
        super(Test_MewloPackObject, self).startup(mewlosite, eventlist)

        # success
        return None









    def signalcallback_test(self, receiverobject, id, message, request, source):
        # we receive a signal callback
        # ATTN: debug test
        msg = "ATTN:DEBUG - From within Test_MewloPackObject, received a signal callback."
        # log it
        self.log_signalmessage(msg, receiverobject, id, message, request, source)
        # return (result, failure)
        return (None, None)







    def updatecheck_checkdatabase(self):
        """
        This function should be implemented by derived classes.
        Check if this pack object needs to run a database update before it can be used.
        :return: tuple (isdatabaseupdateneeded, failure)
        """
        if (False):
            # test to say a db update is needed
            return True, EWarning("TEST: The pack 'test_mpack' needs to run a database update before it can run.")
        return False, None


    def check_isusable(self):
        """
        See base class for documentation.
        """
        # ATTN: test implementation
        databaseversion = self.get_databaseversion()
        if (databaseversion == None):
            self.log_event("Pack 'test_mpack' reporting that it has not yet been installed.")
            self.set_databaseversion(2)
        else:
            self.log_event("Pack 'test_mpack' reporting that it's installed database version is: {0}.".format(databaseversion))
        # TEST: some things to help us test pack settings stuff
        if (True):
            # ATTN: this code should not be done here -- we should not be changing the database in this function
            usecount = self.packsettings.get_subvalue(self.get_settingkey(),'usecount',0)
            self.packsettings.set_subvalue(self.get_settingkey(),'usecount',usecount+1)
            self.packsettings.set_subvalue(self.get_settingkey(),'date_lastuse',datetime.datetime.now())
            if (self.packsettings.value_exists(self.get_settingkey(),'toggleval')):
                self.packsettings.remove_subkey(self.get_settingkey(),'toggleval')
            else:
                self.packsettings.set_subvalue(self.get_settingkey(),'toggleval',1)
        # As a test, say we cannot be run
        if (False):
            return EWarning("TEST: The pack 'test_mpack' needs to run a database update before it can run.")
        # it's good to run
        return None













    def dumps(self, indent=0):
        """Return a string (with newlines and indents) that displays some debugging useful information about the object."""
        str = " "*indent + "Mewlo Test_MewloPackObject reporting in.\n"
        return str

