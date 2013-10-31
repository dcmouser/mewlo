Authentication
==============


Authentication refers to identifying a user, typical via username and password.

While standard username and password are currently the most common method of logging in, there is increasing need to be able to log in using 3rd party services (facebook, twitter, openid).

We want a robust system that supports:

    * username (or email) and password
    * 3rd party "bridged" logins (facebook, twitter, openid)
    * multiple-factor logins (e.g. they need to confirm message received via cellphone prior to session login)
    * requirement of providing BOTH a local password and a bridged login
    * multiple-step logins like seen on bank websites
    * dongle-based logins (paypal key)
    * ability for a user to manage their bridged logins easily, disable some, etc.

Since a user may have multiple ways of logging in (authenticating), we will be using a special table/class for authentication information.

The Authentication model looks like this:

    * UserId: The User ID that this authentification is for
    * AuthEngine: The (internal) Authentication engine class that handles verification of this authentication.  We will have different engines provided by addons to handle the various 3rd party login methods.
    * AuthLabel: A nice displayable label that could be searched on and for identification at a glance.
    * HashedUserIdentifier: This is the unique value returned by the bridged login engine; it enables us to quickly look up the Authentication record when a bridged login is performed.
    * ExtraData: Various data (hashes, salts, etc.) that are used in the authentication (for example hashed and salted password)
    * Enabled: Is this method enabled?

In addition, we probably want some bookkeeping columns like:

    * DateLastUpdate
    * DateLastLogin
    * DateLastLoginFail
    * IPLastUpdate
    * IPLastLogin
    * IPLastLoginFail

One dilemma that I'm chewing over with these bookeeping columns is that they come up in many models -- the desire to track some statistics/log info about date/ip that something was last done, and there are pros and cons to storing this kind of information more generically in separate log-like tables, vs keeping them attached to the model itself.  And i'm not sure what's best.  Part of that answer may depend on whether we will need to be searching/sorting by such info, and how important it is for us to be able to track the last N logins/etc.

My preference would be to use separate tables for such things.


Other notes:

    * When supporting bridged logins, the GUI for user to manage their bridged login info should look like the prototype I made for YUMPS (see screenshot below), where user can see all of their "bridged" login methods and enable/disable, etc.  Sometimes this can get tricky such as needing to ensure at least one login method is left enabled.
    * We also need to handle the case where a user performs a bridged login and we need to decide whether the bridged login should map to a new user account or an existing one.  There is a process in YUMPS to handle this, though people found it slightly confusing.  To elaborate, let's imagine a user who has created an account with a local password and logged in.  They might explicitly say: "Ok i want to add a bridged (facebook) login to this account." -- that would proceed fairly simply.  But let's say they log out and then return to site and choose from the home page "Login/Register using your facebook account", and they click that.. By default the system would think this is a new account but we want to offer them some way before a new account is created (but after they perform the bridged login) of saying "i already have a user account i want to connect this to."
    * There is also an issue with ensuring that no two user accounts are serviced by the same bridged login.
    * We need to be flexible about what information is required for a user.. In many traditional sites (like a forum), a user must specify a password at the time they create their account.  Therefor no user will ever not have a password set.  But in our case it may very well be the case that we want to let users initially sign up and be in some restricted sandbox until they set a password (or other login method).  So we can't make assumptions about the existence of a set password.


