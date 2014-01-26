Redirecting
===========

Redirecting a user from one request to a different page is something that happens frequently in a web app, and there are some subtleties that web frameworks handle in different ways.

For example, one common scenario is a user requests one action, and we need to REDIRECT them to a login page and then BACK to their original request after they log in.

Mewlo offers good support for such temporary redirecting/rerouting.