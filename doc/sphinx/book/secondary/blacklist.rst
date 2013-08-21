Blacklists
==========

In most cms/forum systems there is the concept of a blacklist -- a list of UserIds/emails/ips that are banned from accessing the site for various reasons.

Common features of a blacklist include:

   * Patterns to match on (UserId, email *pattern*, ip *pattern*,etc.)
   * Text note explaining why the blacklist was established
   * Details about date of blacklist addition and who added it

One thing to consider is whether the blacklist and watchlist concepts should be handled by a single entity -- I think probably they should be.  Any patterns we might want to watchlist on, we might want to blacklist on, and vice versa.  And anytime we might want to check watchlist we would want to check blacklist, and vice versa.