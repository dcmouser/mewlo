"""
requests.py
This file holds controller functions that will be invoked by route manager as routes are matched.
"""








def request_login(request, response):
    """Controller function."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('login')
    # then page contents
    response.render_from_template_file('${addon_login_path}/views/login.jn2')
    # success
    return None


def request_logout(request, response):
    """Controller function."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('logout')
    response.add_pagecontext( {'isloggedin':True, 'username':'mouser'})
    # then page contents
    response.render_from_template_file('${addon_login_path}/views/logout.jn2')
    # success
    return None


def request_register(request, response):
    """Controller function."""
    # set page info first (as it may be used in page contents)
    response.set_pageid('register')
    # then page contents
    response.render_from_template_file('${addon_login_path}/views/register.jn2')
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

