Url Routing
===========


URL Routing is found in all web frameworks.

The basic idea is simple enough - a request comes in for a URL.  It may come in through a get or a post.
Parameters may be passed on the url in some combination of modern format like http://www.google.com/search/searchstring AND more traditional format like http://www.google.com?search=searchstring.

The most basic task of the URL router is to take such requests, find the best matching "controller" function, and invoke it.

Some issues to consider:

    There may be some odd cases where one wants to do a full regular expression match on an incoming URL -- but these cases should be RARE and are best avoided in favor of simpler pattern matching.
    It would be nice to provide some internal rewriting of URLs to deal with situations where we want to change a URL pattern.
    It might be nice to log rewriting actions in order to better track the need for such thigns.
    We want to be able to support hosting multiple sites on the same server, and/or moving sites, so it needs to be easy to specify a "prefix" pattern for a site's url matching.
    Every request should have a canonical url and we should not encourage resolution of non-canonical urls.  That is, it is bad to support, as yii does, the idea that parameters in a url can be specified in any order -- their should be a required fixed order of parameters in a url.
    On the other hand, It is common for url parameters to be optional.  So it should be easy to specify a url pattern with named parameters which are optional.
    One common (but somewhat advanced feature) is the need to be able to generate urls for accessing resources in a paged style, or with search filters and sorting options, etc.  Doing this means we often want to programmatically generate a version of the current url, but with added/modified paging/sorting/filtering parameters.
    Keeping with the Mewlo philosophy of favoring standardization and predictability over flexibility, Mewlo is more restrictive than other frameworks regarding URL patterns, so that it can cleanly generate them dynamically.
    Parameters in Mewlo urls should always be specified by name and never position.  So a Mewlo url will never look like "http://www.mewlo.com/archive/2012/june/13" but would instead have to look like "http://www.mewlo.com/archive/year/2012/month/june/day/13".
    If we did want to relax this, we could allow an alternative syntax like "http://www.mewlo.com/archive/{year}/{month}/{day}" where the year,month,day parameter definitions each specified whether the param name is needed or not.
    For such paging/sorting/filtering parameters, we may want to use traditional ? query args and NEVER use such parameters for url routing.
    Should we say that any number of query ? args are always passed through?
    Should we say that query ? args may always be specified in place of normal args.

For how the other guys do it, see:

    https://docs.djangoproject.com/en/dev/topics/http/urls/
    http://docs.pylonsproject.org/projects/pyramid/en/1.0-branch/narr/urldispatch.html


A URL route in Mewlo is made up of:

    An optional unique id name, for reverse url generation.
    A / separated initial path
    An ordered list of parameters.
    Show parameter help for missing and required, or badtype, parameters?
    Optional arguments to pass to request function.
    Accept arbitrary additional named parameters? (useful for dynamic routing)

Entries on the Parameter list take the form:

    Name
    Is required?
    Default value (optional)
    Url format (modern or traditional)
    Help description (optional)
    Type (numeric,string,alpha,alphanumeric,enum,regex, flag)

When a request function (controller) is invoked, parameters (regardless of the form, get, post, traditional, modern) are always passed in a dictionary indexed by name.  Therefore request functions always have the same signature.


If most frameworks support arbitrary regular expression url matching rules, WHY should Mewlo have such a restrictive/prescriptive format for URLs?

There are two answers to this question.

The first answer is that we want to always be able to easily reverse-generate URLs from a request.  That is, we always want to be able to say "given these parameters, create the canonical url for this page".  With arbitrary regex patterned urls, this would only be possible if we gave developer a way to explicitly specify a url generator string (which is a valid solution).

The second answer has more to do with following the philosophy of the approach.  We are trying to encourage, where possible, a single-best-practice approach to doing things, rather than letting people do things a million different ways.  We are favoring consistency and predictability over flexibility.  So in this case we are imposing a "standard" canonical way for urls with parameters to be specified, which discourages doing magic/unusual things, and promotes a scheme that will be easier to maintain and extend as a site evolves.

We can always relax this behavior at some point if we need to, but I'd prefer we keep it if we can.  I think one solution to supporting legacy urls is to allow internal re-writing of regex url requests to standard url formats.  That should give us best of both worlds, plus allow logging of such requests, etc.

In general, however, we should not offer alternative ways to do things simply because the designer prefers it to *LOOK* one way rather than the Mewlo-proscribed way.  Although it runs counter to the idea of accommodating designers, we want to try hard to have a consistent vision that removes stylistic options.