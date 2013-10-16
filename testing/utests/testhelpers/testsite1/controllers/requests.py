"""
requests.py
This file holds controller functions that will be invoked by route manager
"""


# mewlo imports
from mewlo.mpackages.core.mglobals import mewlosite




def request_home(request):
    """Show home page."""
    request.response.set_responsedata("In request_home.")
    return None



def request_about(request):
    """Show about page."""
    request.response.set_responsedata("In request_about.")
    return None



def request_sayhello(request):
    """Show simple hello page; demonstrates use of args."""
    matchedroute = request.get_route()
    args = request.get_route_parsedargs()
    extras = matchedroute.get_extras()
    request.response.set_responsedata("In request_sayhello, with args: {0} and matched route extras: {1}.".format(str(args), str(extras)))
    return None


def request_sayhello_template(request):
    """Show simple hello page; demonstrates use of templates."""
    matchedroute = request.get_route()
    args = request.get_route_parsedargs()
    extras = matchedroute.get_extras()
    # create template
    template = mewlosite().templater.from_file('${siteviewpath}/hello.jn2')
    templateargs = {'args':args, 'name':args['name'], 'age':args['age']}
    # render template
    renderedtext = template.render_string(templateargs)
    request.response.set_responsedata(renderedtext)
    return None



def request_article(request):
    """Show an article."""
    request.response.set_responsedata("In request_article.")
    return None




