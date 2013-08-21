Messages and Mailboxes
======================


We want to support the ability of users to send messages to each other and to receive system messages.  These should typically act like an internal mail system (in addition to receiving copies via normal email).

So one use case is when users send messages to other users.
Another is when the system wants to send a message to one or more users to alert them of some information.

There are a few delicate issues that we must solve for where we want to send a message to 500,000 users..

For the normal case, we will have 3 models:

   * MailboxFolder - A hierarchical collection of custom user-created folders (each user can create their own custom folders), that the user can use to file incoming and outgoing messages into.
   * SentMessage - Contains the actual text of an outgoing message and can be "heavyweight" because relatively few outgoing messages will be created.
   * ReceivedMessage - A very "lightweight" model that must be created for every recipient of every message.  So if the system sends a message to 500,000 users, we will have to create 500,000 of these rows.

Other details:

We may want to support some additional special kinds of system-messages using this system, while handling them slightly differently. For example we may want to support some system messages that, instead of being displayed in user's mailbox and emailed to them, would be displayed like a warning message on every page until acknowledged, at which point it might be deleted (for example a message about change of system policies, etc.)