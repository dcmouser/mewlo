Signal Dispatcher
=================


The MewloSignalDispatcher is a central object responsible for allowing core and 3rd party addons to register that they want to send or receive (subscribe to) signals (aka messages/events), and then supports the broadcasting of such signals to all subscribed listeners.
Signals contain messages that can have arbitrary content, and broadcasters can collect return values if they like.
A filtering system allows subscribers to specify which signals they want to listen to, from particular sources, etc.

The signal dispatcher is how most communication with addons is handled, and how most modification to default behavior by 3rd party addons is accomplished.


See also:

   * The Mewlo Component Registry system.