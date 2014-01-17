"""
msignal.py
This module contains classes and functions for the signal sending/receiving system.

The Signal system implements a kind of slot-filler, subscriber-receiver model, so that we can have many-to-many signal sending without senders needing to know about recipients.

Here's how it works:

A SignalDispatcher object is the central manager of all signals incoming and outgoing.

Arbitrary objects can register (with the dispatcher) in order to broadcast signals (they send them to the dispatcher);
 note that registering in this case does little -- ATTN:TODO add more about why to do this?

Arbitrary objects can register (with the dispatcher) in order to subscribe to receive signals matching certain criteria.

To receive messages, one creates a SignalReceiver object (essentially a wrapper) which specifies a callback function,
 a filter to define which singals to send, and additional parameters to pass to the callback function.

To broadcast a signal message, one simply calls the dispatcher broadcast function and provides:
    * id - a dotted path string representing the signal's name; the most common scenario will be when receivers match on exact signal message names.
    * message - arbitrary object representing the message contents; convention will dictate the type and contents.
    * request - reference to the current request being processed (useful to have for various things like logging)
    * source - a dotted path string representing the signal's "source"; convention may dictate use; can be useful as another field for filtering by recipients.
    * flag_collectresults - if True then a list collecting the the return values from the recipients will be returned; list is of tuples (returnval, failure)

There are some details of importance:

    * Rather than use a strict interface-signature typing to ensure that signals are parameterized correctly.
    * Instead, we use a very generic approach to signal formats; this makes things simpler and easier
    * But this puts more burden on subscribers to be careful processing passed signal parameters
    * We favor simplicity and avoid magic stuff that happens automatically; we do not auto-register signals.
    * The closest similar python implementation can be found in Django signals
    * We want to be as efficient as possible when we can be.


ATTN:TODO - There is a lot more to implement here.

"""


# mewlo imports
from ..manager import manager


# python imports





class MewloSignalReceiver(object):
    """The object receives signals from dispatcher."""

    def __init__(self, owner, callback, idfilter, sourcefilter, extra = None, flag_returnsvalue = True):
        """Constructor."""
        # init
        self.owner = owner
        self.callback = callback
        self.idfilter = idfilter
        self.sourcefilter = sourcefilter
        self.extra = extra
        self.flag_returnsvalue = flag_returnsvalue


    def startup(self, mewlosite, eventlist):
        #print "**** IN SIGNALRECEIVER STARTUP ****"
        pass

    def shutdown(self):
        #print "**** IN SIGNALRECEIVER SHUTDOWN ****"
        pass



    def does_want_signal(self, id, message, request, source):
        # we will want to be more elaborate about this later, for now we check exact match of id
        if (id == self.idfilter):
            return True
        if (self.idfilter=='*'):
            return True
        return False


    def handle_signal(self, id, message, request, source, flag_collectresults):
        """
        The receiver MUST receive a call of the form:
            * callback(thisSignalReceiver, id, message, source)
        The self.flag_returnsvalue tells us whether we should expect the callback to return a tuple of (result,failure) format
        For the format of id, message, source, see broadcast() function below.
        The thisSignalReceiver reference points to the receiver that was registered to receive the signal; it can be used to maintain and look up arbitrary data.
        """
        # invoke it and expect a tuple return
        if (flag_collectresults and self.flag_returnsvalue):
            # call and return
            (result, failure) = self.callback(self, id, message, request, source)
        else:
            # call and ignore return
            self.callback(self, id, message, request, source)
            result = None
            failure = None
        # return result
        return (result, failure)



    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "SignalReceiver (" + self.__class__.__name__  + ") reporting in.\n"
        indent += 1
        outstr += " "*indent + "idfilter: "+str(self.idfilter)+"\n"
        outstr += " "*indent + "sourcefilter: "+str(self.sourcefilter)+"\n"
        outstr += " "*indent + "extra: "+str(self.extra)+"\n"
        outstr += " "*indent + "flag_returnsvalue: "+str(self.flag_returnsvalue)+"\n"
        outstr += " "*indent + "callback: "+str(self.callback)+"\n"
        return outstr









class SignalSender(object):
    """The object that sends signals to the receiver."""

    def __init__(self):
        """Constructor."""
        # init
        pass

    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "SignalSender reporting in.\n"
        return outstr

























class MewloSignalManager(manager.MewloManager):
    """The signal dispatcher."""


    def __init__(self):
        """Constructor."""
        super(MewloSignalManager,self).__init__()
        # init
        self.signals = []
        self.senders = []
        self.receivers = []


    def startup(self, mewlosite, eventlist):
        super(MewloSignalManager,self).startup(mewlosite,eventlist)
        # and now the receivers and senders
        # ATTN: problem -- receivers are not created yet at this time, so this code is useless
        #print "ATTN: in signal dispatcher startup with {0} receivers.".format(len(self.receivers))
        for receiver in self.receivers:
            receiver.startup()
        for sender in self.senders:
            sender.startup()

    def shutdown(self):
        super(MewloSignalManager,self).shutdown()
        #print "** SIGNAL DISPATCHER IS SHUTTING DOWN. **"
        self.unregister_all()


    def register_sender(self, sender):
        """
        This function is called ONCE by a component that it might send/broadcast signals.
        ATTN: for now we don't use this
        """
        self.senders.append(sender)


    def register_signal(self, signal):
        """
        This function is called ONCE by a component to describe/advertise a kind of signal that it might send.
        This function serves to aid documentation -- it simply provides information that we could use to keep track of potential signals.
        It may also provide meta information to potential listeners.
        ATTN: for now we don't use this
        """
        self.signals.append(signal)



    def register_receiver(self, receiver):
        """
        This function is called ONCE by a component that wishes to received signals (of a certain kind and/or by a certain sender).
        This is currently the only one of the register functions that we bother with; the others are not important.
        """
        self.receivers.append(receiver)




    def broadcast(self, id, message, request, source, flag_collectresults = False):
        """
        An object calls this function whenever it wants to broadcast a signal to all listeners.
        :id: Dotted string representing signal name
        :message: The signal message contents (could be a string or any arbitrary object; common case would be to pass a dictionary); convention dictates use
        :source: None | Dictionary described "source" of message, which can be used to filter by receivers; convention dictates use
        :flag_collectresults: If True, then the results from every called receiver will be collected and returned as a list of tuples
        """

        # for collecting return value
        if (flag_collectresults):
            retv = []
        else:
            retv = None

        # we will eventually want to be much more efficient about this, and use a hash maybe for signal ids.
        # for now we will just iterate all
        for receiver in self.receivers:
            if (receiver.does_want_signal(id, message, request, source)):
                # ok it matches, so deliver it
                result, failure = receiver.handle_signal(id, message, request, source, flag_collectresults)
                # collect results? if so add tuple to result list
                if (flag_collectresults):
                    retv.append( (receiver, result, failure,) )

        # return
        return retv



    def unregister_byowner(self, owner):
        """Unregister anything owned by the specified ownerobject."""
        self.receivers = [x for x in self.receivers if not self.shutdown_obj_ifownedby(x,owner)]

    def shutdown_obj_ifownedby(self, obj, owner):
        """If a component has the owner specified, shut it down and return True; otherwise return False."""
        if (obj.owner != owner):
            return False
        obj.shutdown()
        return True

    def unregister_all(self):
        """Shutdown all registered receivers."""
        #print "***SHUTTING DOWN REGISTERED RECEIVERS: "+str(len(self.receivers))
        for receiver in self.receivers:
            receiver.shutdown()
        self.receivers = []



    def dumps(self, indent=0):
        """Debug information."""
        outstr = " "*indent + "Signal Dispatcher (" + self.__class__.__name__ + ") reporting in.\n"
        indent += 1
        outstr += " "*indent + "Registered Signals: "+str(len(self.signals))+"\n"
        for signal in self.signals:
            outstr+=signal.dumps(indent+1)
        outstr += " "*indent + "Registered Signal Senders: "+str(len(self.senders))+"\n"
        for sender in self.senders:
            outstr+=sender.dumps(indent+1)
        outstr += " "*indent + "Registered Signal Receivers: "+str(len(self.receivers))+"\n"
        for receiver in self.receivers:
            outstr+=receiver.dumps(indent+1)
        return outstr


