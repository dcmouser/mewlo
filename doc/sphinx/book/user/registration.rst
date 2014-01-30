Registration
============

Registering a new account on a website can be done in many different ways, and Mewlo aims to provide the best registration experience and options.

Let's look at some common ways that sites let users register new accounts.



Username, Password, and Email
-----------------------------

The traditional way that users register on a site is by choosing a unique username and password, and providing an email address which must be verified before they can log in.
The user account is created immediately byt the user cannot login until the email is verified.  Before completing verification they may request resending of the verification email or change their emal (providing they remember their password).

Notable aspects: User must provide these 3 pieces of information (and is often asked for additional information like real name, etc.) before continuing.  A captcha is often provided to discourage bots.

Disadvantages: If they specify their email wrong, they sometimes don't know what to do and regret having to re-enter the info again in creating a whole new account -- especially given that the username they first signed up with is now in use.



Multistep with Email first
--------------------------

An alternative to getting a bunch of information up front is simply to let user provide their email address and verify that first, before even bothering creating a user account.
After the user verifies their account, we can require them to choose a username and password.

Notable aspects: Very quick to sign up.  Might be a more consistent approach if we want to gather additional user profile information -- that is, the more extra profile information we need to gather, the more appealing this approach.

Advantage: No need to create user accounts for people until they verify their email address -- should cut down on mistaken email registrations.  No need to reserve usernames until email is verified.  No need to prune abandoned user accounts.

Disadvantages: May be somewhat confusing for users accustomed to conventional approach.  Might appear more like a spam sending site to those hesitant to give out their email address (i.e. may appear to focused on gathering emails).

Summary of workflow:
    * Registration form asks only for email address (and optional captcha).  If desired, we can collect additional information (but just store it in verification object).
    * Submission creates an entry in the Verification table of type PendingUserAccoutnViaEmail -- does NOT create a new user account at this time.
    * The verification entry causes an email to be sent to user with a long verification link (or a short one that also requires email address?).
    * If user does not visit verification link it will expire in [N] days.
    * User may at any time come back and put their email in again to re-try the registration process; existing verification entry would be replaced.
    * After the verification link is visited, the verification entry cannot yet be consumed. Instead the user is presented with a form to fill out their username (and password typically).
    * Only after we have a valid username and password can we consume the verification entry and create the user account.
    * At that point, there may be additional form pages with profile fields that we may want to present like a (possibly postponeable) wizard.



Variation on Email first, using short typed code
------------------------------------------------
Note: I have seen sites that email (or mobile phone) a SHORT verification code (say 4 characters) for creating new user accounts, that the user TYPES into a box like a captcha to CONTINUE the registration process; in this case, the code does not have to be unique or long/secure because it is only valid when combined with the current user's SESSION.




Bridged Account Creation
------------------------

Here we let a user create an account on the site by signing in with a 3rd party authentification (bridged account), for example using OpenId, or their Facebook, Google, or Twitter accounts.

Bridged accounts can be highly appealing for some users, because it means they have less passwords to remember and can bring accross other identity information (name, email).

While the low-level steps of doing authentication through 3rd party sites is complicated, their are existing libraries to do this that we would rely upon.

See the help section on Bridged Logins for more information about options we need to provide user to manage their bridged logins after creation.

Advantages: Some users prefer this and it may offer one of the fastest registration processes.
Disadvantages: We are not guaranteed to have a valid (or any) email address for a user.  This can be problematic and requires extra logic in many operations if we cannot assume all users have a verified email address.  Requires additional complex options to allow user to manage their bridged login(s).



High-security Account Creation
------------------------------

There are some scenarios (like financial sites) that tend to follow a more cumbersome signup and registration process.

Extra steps in the registration process can involve choosing a unique identifier image (and associated passcode) which can serve to prove to the user that they are providing their credentials to the true site.




Additional Profile Fields
-------------------------

Depending on the website, their may be additional profile fields we want to get from the user at the time of registration (rather than in some separate voluntary profile editing).
Let's consider some different scenarios, and some back-end needs related to them:

    * We have some custom user profile fields we REQUIRE the user to fill out prior to registering (e.g. full user name); we would like the registration procedure to create the account with these extra fields without require a lot of extra work.  This may include fields that are file uploades (avatar for example).
    * We want to step the user through some additional profile editing pages (some fields optional and some required), and not let them into their account until they fill them out.

