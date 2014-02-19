Verifications
=============

The most common use of verifications (or validations) can be seen on all websites with user accounts:

The user signs up, usually by specifying a username, email, and password.

The user's account is then created, but the user cannot login yet.

The site sends an email to the user with a special code/link that the user must visit in order to "verify" (validate) their email address.



Why verify?
-----------

There are several reasons for requiring verification of an email address:

    * It's usually very important that every account on the site has a valid working email address -- in order to reset a forgotten password, or to be notified about important events.
    * If we don't verify the email address, people could provide the emails of other people, leading to unwanted spamming.
    * Requiring a valid email cuts down (somewhat) on automated bot accounts.



Other times we might use a verification system
----------------------------------------------

Most online verification is about emails.  In addition to verifying a new-account email, a similar (but different) process is used when users want to *change* their email address. In that case the account remains active and the OLD email is retained and used until the new one is verified.

On some sites, we can see other kinds of more involved verification procedures:

    * On sites like paypal, where the site may need to send or deposit money into a bank account, special procedures are sometimes used to verify the owner of a bank account (making a random deposit of a few cents in the user's bank account and asking user to verify the amount deposited).
    * On some sites that rely on user's proving their real life identity, a procedure may be in place to verify the person is who they say they are.
    * Some sites will accept a user phone number, and call with a voice or text code that the user must provide.  This proves that the phone belongs to the user, but can also be used as an alternate way to verify account holder status when resetting passwords, etc.
    * Some sites allow users to specify multiple emails, and all must be verified.
    * Some operations ask the user for a long (globally unique) verification link.
    * Other operations may use a very short code (4 characters) that can easily be sent via email or phone message.  Typically one could use a small code when it can only be provided by a single, already signed in user -- or it is tied to the person's session (which doesnt require a user account be created yet).
    * Some sites may require verification by snail mail (code is sent in mail), and/or may require submission of proof of identity by user through mail/fax.



A general purpose verification system
-------------------------------------

Mewlo uses a centralized verification table for keeping track of all verifications.

A verification entry stores standard information like the verification code, request date, expiration date, request ip, userid, TYPE of verification (string value), and arbitrary serialized data related to the verification.

The verification system takes care of checking for expirations of verification entries and general bookkeeping.

For verifications like email registration/change, the verification entry itself will have the name and value of the field to be changed.  As such it contains complete information about the pending change, and will be the ONLY record of some change requests).

For example, if a user asks to change their email, we might query for such pending verification entries when displaying their profile to show things like ("requested change to email address xxxx on jan 1, 2013; pending verification)."




Keeping track of verified fields
--------------------------------

The verification table is used to keep track of PENDING verification requests.  It is not meant to keep track of verifications once they have been completed.

On a typical website, where only email addresses are ever verified, a user model typically has a dedicated boolean field for "is_email_verified".

There may be times when a site wants to keep track of the verification state (and proof details) for multiple fields (mobile phone, address, bank account, secondary emails).

In such a case, we have some options:

    * use a dedicated "is_fieldx_verified" in the user account (not very scalable)
    * use a generic user-profile field table (supporting arbitrary profile data), and give each entry not only a value, but a boolean verified flag and possibly extra proof details.
    * use a verification-proof table, that is specifically designed for tracking what information has been verified and when/how.  this could be used with dedicated or separate-profile-table user account fields.

The only really uncomfortable aspect of this is the tradeoffs when dealing with very common fields, like user email.  such a common field is best handled with a dedicated field in the user account, not via separate table of profile fields, etc.





Some verification types
-----------------------

PreUserCreationVerificationType - When verified, this allows a client to create a new user account.  The entry can contain contain a list of fields/properties for the new user account, that were set at the time the verification entry was creation.  One of these fields will be the actual field that we trust has been verified (usually email but could be mobile phone).  The other fields may simply be values we collected from the user at the time of signup for convenience.  For those fields, we MAY want some to be locked -- while others may be simply used as defaults.

UserPropertyVerificationType - When verified, this entry specifies one or more user properties that have been confirmed.  The most common use of this might be when user requests a change of their email address, but it could also be used for verifying a mobile phone, etc.





Verification urls
-----------------

One question with verifications is whether we prefer having a central url where verifications are resolved, regardless of their type and source, or whather we wean want to use different urls for different verifications.

A central url would mean that addons/plugins would have to be triggered from this central url, but would allow a concise short url for verification. 