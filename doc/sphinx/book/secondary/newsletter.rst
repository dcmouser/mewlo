Newsletters
===========


It's common for a website to want to send newsletters (perhaps multiple differently subscribed newsletters) out by email.

This can be a non-trivial action when we have hundreds of thousands of people we want to email.

An open question is the degree to which newsletter functionality can be shares with the User Messaging system. There may be a need to have newsletter subscribers who are NOT registered users, and some users who may want to subscribe or unsubscribe to certain newsletters.  This complicates things.    There is also a question of whether a newsletter email should also be delivered as an internal message

But in many ways the actual management of recipients shares underlying functionality of needing to be able to stagger/schedule the sending of large numbers of emails.

Suggested models:

   * NewsletterListGroup - Defines a particular target audience group that newsletters can be directed to.
   * NewsletterMessage - The actual text message of a newsletter that will be sent to one or more NewsletterListGroup.
   * NewsletterSubscriber - Represents an individual who may be subscribed to one or more NewsletterListGroups.  This may be a pointer to a Mewlo *USER* or a standalone email.
   * NewsletterTracks - Keeps track of what messages have been sent to what Subscribers and any events we need to keep around (possibly only temporarily).