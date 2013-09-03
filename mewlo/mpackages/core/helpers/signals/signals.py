"""
signals.py
This module contains classes and functions for the signal sending/receiving system.

Here's how it works:

Arbitrary objects can broadcast signals (they send them to the dispatcher).
Arbitrary objects can register (with the dispatcher) in order to subscribe to receive signals matching certain criteria.

There are some details of importance:

    * Rather than use a strict interface-signature typing to ensure that signals are parameterized correctly.
    * Instead, we use a very generic approach to signal formats; this makes things simpler and easier
    * But this puts more burden on subscribers to be careful processing passed signal parameters
    * We favor simplicity and avoid magic stuff that happens automatically; we do not auto-register signals.
    * The closest similar python implementation can be found in Django signals
    * We want to be as efficient as possible when we can be by

"""


# helper imports

# python imports







class SignalReceiver(object):
    """The object receives signals from dispatcher."""

    def __init__(self, callback, idfilter, sourcefilter, extra = None, flag_returnsvalue = True):
        """Constructor."""
        # init
        self.callback = callback
        self.idfilter = idfilter
        self.sourcefilter = sourcefilter
        self.extra = extra
        self.flag_returnsvalue = flag_returnsvalue


    def does_want_signal(self, id, message, source):
        # we will want to be more elaborate about this later, for now we check exact match of id
        if (id == self.idfilter):
            return True
        if (self.idfilter=='*'):
            return True
        return False


    def handle_signal(self, id, message, source, flag_collectresults):
        """
        The receiver MUST receive a call of the form:
            * callback(thisSignalReceiver, id, message, source)
        The self.flag_returnsvalue tells us whether we should expect the callback to return a tuple of (result,failure) format
        For the format of id,message,source, see broadcast() function below.
        The thisSignalReceiver reference points to the receiver that was registered to receive the signal; it can be used to maintain and look up arbitrary data.
        """
        # invoke it and expect a tuple return
        if (flag_collectresults and self.flag_returnsvalue):
            # call and return
            (result, failure) = self.callback(self, id, message, source)
        else:
            # call and ignore return
            self.callback(self, id, message, source)
            result = None
            failure = None
        # return result
        return (result, failure)







class SignalSender(object):
    """The object that sends signals to the receiver."""

    def __init__(self):
        """Constructor."""
        # init
        pass



class Signal(object):
    """The object that represents a kind of signal."""

    def __init__(self):
        """Constructor."""
        # init
        pass









class SignalDispatcher(object):
    """The signal dispatcher."""



    def __init__(self):
        """Constructor."""
        # init
        self.signals = []
        self.senders = []
        self.receivers = []
        pass




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




    def broadcast(self, id, message, source, flag_collectresults = False):
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
            if (receiver.does_want_signal(id, message, source)):
                # ok it matches, so deliver it
                result, failure = receiver.handle_signal(id, message, source, flag_collectresults)
                # collect results? if so add tuple to result list
                if (flag_collectresults):
                    retv.append( (receiver, result, failure,) )

        # return
        return retv







    def dumps(self, indent=0):
        return indent*" " + str(self)


