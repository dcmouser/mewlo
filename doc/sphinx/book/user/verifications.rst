Verifications
=============


There are various places where we need to VERIFY/VALIDATE some information that a user has provided, for example:

    * Verifying that a user's email address is valid (at initial signup and then again when changing email).
    * Verification of user's bank account, phone number, website ownership, etc.
    * Verification of a request (by sending them an email to confirm it, etc.)

The Verification model is responsible for such things.

Essentially Verification works in four asynchronous phases:

    * First, a piece of Mewlo code creates a Verification request event.
    * Second, the Mewlo Verification model must generate whatever test is needed and alert the user to expect such a test and how to reply.
    * Third, when the user completes a verification, the Verification model needs to alert the code via a callback with details of result.
    * Fourth, if a verification test expires without being completed, the Verification model needs to alert the code via callback with event signifying test expiration.