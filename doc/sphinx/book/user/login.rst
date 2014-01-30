Login
-----

This will discuss login options.



High-security Logins
--------------------

There are several options for high-security logins.

One additional layer of security can be a key fob that generates unique identifications (paypal uses these).
Another option for increased security is to mail (or text message) a unique fast-expiring code each time the user needs to login (or after some interval expires); although this makes logging in somewhat more cumbersome, it does significantly add security to logins.

In some cases, we don't need to perform extra security just to let user log in and access most features of their account -- but we do want to use higher security (if they haven't proven their session with higher-security recently) before letting the user do some operations.

There are other ways that login security can be improved.  One obvious step is forcing all login/registration to be done over https/ssl.  Another trick (used by SMF) is to have the user's client browser do the password hashing client-side.


Bridged Logins
--------------

I use the term "Bridged Login" to refer to any process through which the user logs into a Mewlo site using credentials from another site.

The most common example of bridged logins can be seen on websites where you can login, and automatically create an account in the process, by authenticating with a 3d party, for example the users account on google, facebook, openid, or twitter.  OpenId being an example of a dedicated protocol for bridged logins.

The 3rd party provideds the authentification and initial account information.

We would also like any Mewlo site to be able to act as an (OpenId) provider to prove identity to other sites; for Mewlo-to-Mewlo sites, we would like to provide rich arbitrary user account information agreed to by both sites.
