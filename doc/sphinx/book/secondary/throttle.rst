Throttling System
=================


The Throttling system provides an API that can be used to easily and efficiently keep track of events that might happen too frequently, and allow code to detect and react to degenerate conditions.

For example, if we are sending an administrator an email everytime a serious error occurs, we might use a throttler that ensures that the system does not try to send 10000 errors within the source of 60 seconds if things go terribly wrong.

The Throttling system provides an API to keep track of the rate of some events and disable it at certain rates -- while notifying when such throttles kick in, etc.

The throttling system would also be used to blacklist hammering/DOS attacks, kick-in to temporarily deny web spiders, etc.

The throttling system also exposed API to inspect the server load, and respond differently (or alert/log) based on the current/average server/database/memory/cpu load.