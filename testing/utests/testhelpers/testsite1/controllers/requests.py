"""
requests.py
This file holds controller functions that will be invoked by route manager as routes are matched.
"""








def request_home(request, response):
    """Show home page."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('home')
    # then page contents
    response.render_from_template_file('${siteviewpath}/home.jn2')
    # success
    return None






def request_help(request, response):
    """Controller function."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('help')
    # then page contents
    response.render_from_template_file('${siteviewpath}/help.jn2')
    # success
    return None

def request_contact(request, response):
    """Show contact page."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('contact')
    # then page contents
    response.render_from_template_file('${siteviewpath}/contact.jn2')
    # success
    return None

def request_about(request, response):
    """Show about page."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('about')
    # then page contents
    response.render_from_template_file('${siteviewpath}/about.jn2')
    # success
    return None







def request_sayhello(request, response):
    """Show simple hello page with some arguments."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('hello')
    # then page contents
    args = request.get_route_parsedargs()
    templateargs = {'args':args, 'name':args['name'], 'age':args['age']}
    response.render_from_template_file('${siteviewpath}/hello.jn2', templateargs)
    # success
    return None





def request_article(request, response):
    """Show an article."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('article')
    # then page contents
    response.render_from_template_file('${siteviewpath}/article.jn2')
    # success
    return None

