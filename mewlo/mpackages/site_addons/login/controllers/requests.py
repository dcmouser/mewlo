"""
requests.py
This file holds controller functions that will be invoked by route manager as routes are matched.
"""



# mewlo imports
from ..loginhelper import LoginHelper

# python imports






def request_login(request, response):
    """Controller function."""
    # login helper
    lhelper = LoginHelper(request, response)
    # then page contents
    return lhelper.renderpage_login()





def request_logout(request, response):
    """Controller function."""
    # login helper
    lhelper = LoginHelper(request, response)
    # then page contents
    return lhelper.renderpage_logout()





def request_register(request, response):
    """Controller function."""
    # login helper
    lhelper = LoginHelper(request, response)
    # then page contents
    return lhelper.renderpage_register()
















