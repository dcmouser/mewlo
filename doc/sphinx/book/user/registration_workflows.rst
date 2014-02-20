Registration Workflows Contd.
=============================

In previous help section I went into a lot of detail on different registration methods.  Here I will try to summarize briefly the registration options available.


Immediate account creation
--------------------------

    * When the user registers, they provide username, email, password.  
    * The username+email are checked to be unique, and if so, the user database object is created immediately.
    * The user's email field is marked as non-verified.
    * A verification email is sent to verify the user's email address.
    * Until the email address is verified, it cannot be trusted.
    * Until the email address is verified, some sites might let user log in but not access most areas (less common); some sites might prevent user from even logging in (more common).
    * Until the email address is verified, the user can request a new verification email be sent.
    * Until the email address is verified, the user can change his email address -- either by proving their username+password or by session id.
    * Other new users cannot register another account with same username or email, even if email address is not yet verified.
    * If an email address is not verified within some timeframe, we may want to delete it, and or send the user a reminder email.
    * In some unusual cases we might use mobile phone numbers instead of email addresses, etc.; other details remain the same.
    * Benefits: If desired, users can create limited accounts without ever proving email; more traditional approach.
    * Drawbacks: Spurious creation of abandoned accounts; reserves abandoned email addresses; users asked to provide too much information on initial registration.


Deferred account creation
-------------------------

    * When user registers, they provide their email and possibly nothing else (though optionally we may want to let them provide more and cache it).
    * The information provided (email and username if provided) is checked to be unique, and if so, they are emailed a pre-account-creation verification email.
    * Until they verify the receipt of that email, no account will be created and others are free to (re) register with the same email address (username, etc.).
    * When the user verifies the receipt of the pre-account-creation email, they are presented with a more detailed registration form.  The verificaiton code is not yet consumes.
    * This registration form is prefilled with the info they provided at initial signup (possibly only email).  The email address verified is read-only and any forced form manipulation of this field will be igored.
    * The user may now have an opportunity to provide additional information like username, password, etc.
    * The form contains the verification code as a hidden field.
    * When they submit this more detailed registration form, the username and email address (and any other unique fields) are checked to be unique.
    * Assuming all is well, the new account is created and the email address is marked as verified.
    * Benefits: Initial signup is easy, requiring only an email address; no polution of abandoned user accounts; no reservation of abandoned email addressed; if user provided wrong email address they can just repeat with correct one; we can pre-submit default registrations for people that they can modify or ignore.
    * Drawbacks: More complicated; non-traditional approach may be confusing to user; not suitable for when you want limited user accounts created even in absense of email verification.


Developer decisions
-------------------

Let's look at the decisions a developer needs to make regarding the registration workflow:

    * Will you use immediate or deferred account creation?
    * What will the "full" registration page look like -- what fields will be on it?
    * If using deferred account creation, what will the pre-registration page look like -- what fields will be on it?  What field will be used to verify (currently only email supported).
    * If using deferred account creation, do you want to use long or short verification coders?  Short codes are tied to a session.

