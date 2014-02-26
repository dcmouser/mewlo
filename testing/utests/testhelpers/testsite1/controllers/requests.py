"""
requests.py
This file holds controller functions that will be invoked by route manager as routes are matched.
"""








def request_home(request):
    """Show home page."""
    # set page info first (as it may be used in page contents)
    request.response.set_renderpageid('home')
    # then page contents
    request.response.render_from_template_file('${siteviewpath}/home.jn2')
    # success
    return None






def request_help(request):
    """Controller function."""
    # set page info first (as it may be used in page contents)
    request.response.set_renderpageid('help')
    # then page contents
    request.response.render_from_template_file('${siteviewpath}/help.jn2')
    # success
    return None

def request_contact(request):
    """Show contact page."""
    # set page info first (as it may be used in page contents)
    request.response.set_renderpageid('contact')
    # then page contents
    request.response.render_from_template_file('${siteviewpath}/contact.jn2')
    # success
    return None

def request_about(request):
    """Show about page."""
    # set page info first (as it may be used in page contents)
    request.response.set_renderpageid('about')
    # then page contents
    request.response.render_from_template_file('${siteviewpath}/about.jn2')
    # success
    return None







def request_sayhello(request):
    """Show simple hello page with some arguments."""
    # set page info first (as it may be used in page contents)
    request.response.set_renderpageid('hello')
    # then page contents
    args = request.get_route_parsedargs()
    templateargs = {'args':args, 'name':args['name'], 'age':args['age']}
    request.response.render_from_template_file('${siteviewpath}/hello.jn2', templateargs)
    # success
    return None





def request_article(request):
    """Show an article."""
    # set page info first (as it may be used in page contents)
    request.response.set_renderpageid('article')
    # then page contents
    request.response.render_from_template_file('${siteviewpath}/article.jn2')
    # success
    return None

