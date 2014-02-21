Verified Profile Fields
=======================

On many (most?) websites with user accounts, user accounts are created at registration, and marked as having an UNVERIFIED email address.
Typically, the user must verify their email address by clicking on a link (or provided a code) that was sent to the email address they provided at signup.
The user account will typically have a "is_email_verified?" field for tracking this information.
Until the user verifies their provided email address, it is treated as untrusted -- HOWEVER it will be displays to administrators for maintenance operations and searching, etc.

Now when a user wishes to CHANGE their email address, the process is different.  The user requests the change of email, but their actual profile email is NOT changed at that time.
Instead, the user is emailed a verification code, and only when that verification code is provided, is the actual email changed.  Until then the newly requested email is essentially invisible (and untrusted) in the system.

Some web services make use of additional profile fields that require some form of verification:

    * Mobile phone numbers
    * Bank accounts
    * Additional email addresses
    * Physical addresses
    
These additional profile fields suggest that having dedicated "is_FIELDNAME_verified?" columns is unscalable.


What other alternatives do we have to verifying and keeping track of verified profile fields?

I propose the following:

    * Email address be treated specially and traditionally.
    * Other fields may be stored EITHER as dedicated fields or in special table of name-value pairs
    * The name-value pair table will have a column for whether the field value has been verified (and perhaps extra info like data and manor of verification, expiration, etc.)
    * The name-value pair table can be used to hold verification info even for fields that exist as dedicated columns.