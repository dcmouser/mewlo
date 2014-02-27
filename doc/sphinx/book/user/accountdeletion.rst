Account Deletion
================

The deletion of user accounts serves as a great example of how things that my seem simple on first glance, can actually be quite complicated and involve many decisions and options.

The naive approach
------------------

Let's start with a naive view of user account deletion, and then see where things go wrong.

A user registers on a site, creates their account (resulting in the creation of a User object in database).
They log in, do some stuff, create some content, and then later decide they no longer want to be a member of the site.
They go to their profile, choose to delete their account, and we delete their User object.


What goes wrong
---------------

What's wrong with this naive approach?

The most immediate problem with this approach is that the user has created content, which will inevitably be linked to that user id.

If we delete the User object, the content now refers to a missing user author -- we no longer have the author's name or any info about them.
In some cases, the solution to this is to delete all content created by the user -- though in many cases that is not what we want.
Some content (such as messages sent between users), we do not even have the option of deleting the content refering to the user because their are other users that are tied to the content.
In some cases, we need to perform more elaborate changes of ownership of content.  For example, if the user was the owner of an active "group" or "project", then we need to transfer ownership of such resources to someone else.

Stepping back a bit -- it is sometimes the case that we do not wish to even let users delete accounts, at least not without some human verification/involvement by a moderator to ensure that the account.  It may be that a moderator must make decisions about how to deal with content created by the user.  Or it may simply be that a moderator should communicate with the user to see if account deletion is really the best option.

Real account deletion (deletion of the user object) has security ramifications as well.  Once deleted, we (potentially) lose all data we may have stored about the user's access patterns, ip addresses, logs.  We also make the login name and email available to new registrations, which could cause confusion if the user was well known and established.

For all of these reasons, a more appealing solution is often to *VIRTUALLY* "delete" the user, simply by marking the account as "deleted" but not actually removing the user object from the database.

In such a scenario, we have options about how invisible to make the user from queries.  In the extreme case we could make them invisible and unrecoverable in nearly all operations (searching, etc.).  In more liberal cases we might simply keep the account as it was but simply indicate that it has been disabled/deleted.  In most cases we will probably want the account visibile to high-level moderators.

One difficulty with keeping the account visible (but marked as deleted) to the public is that sometimes users are insistent that their account and information be "completely removed" for privacy reasons.  So it may be desirable to have a way both to mark user accounts as "disabled", in which case they are visible as normal but can't be actually used, and also "virtually deleted" in which case they should be completely invisible to all normal users (except perhaps to the extent that new users cannot register with the deleted user's name or email or other unique fields).

Now, there may be some cases where a complete deletion of a user account (along with any content created by user) is appropriate and feasible.  A common case would be for a spammer who creates an account and makes a few spam posts.  In such a case, a one-step complete deletion of account and user-created-content may be appropriate (though we may want to record/report some information about the spammer for our records).


A more realistic approach
-------------------------

Mewlo adopts the following approach to user account deletion.

First, users have an easy way of submitting an account-deletion request.  This is important because users get frustrated if they can't find a way to do this.

From this request they can specify why they are deleting their account, and may choose to simply disable it instead.

If they request to formally and completely delete their account, we still only disable their account and leave their content visible; an option here would be to virtually delete their account but still leave their content visible.

A moderator is then notified about the user's deletion request (they are added to moderator review queue).

The moderator is presented with a summary of user's content and can choose from options that include doing nothing other than leaving the account disabled, to marking all content created by the users as virtually deleted, to actually deleting the account completely along with all associated content.

Disabled and virtually deleted accounts can be restored by a moderator at any time.