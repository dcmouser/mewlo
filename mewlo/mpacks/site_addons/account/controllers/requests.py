"""
requests.py
This file holds controller functions that will be invoked by route manager as routes are matched.
"""



# mewlo imports
from ..accounthelper import AccountHelper

# python imports






def request_login(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_login()





def request_logout(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_logout()





def request_register(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_register_deferred()














def request_verify_registration(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_verify_registration_deferred()


def request_register2(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_state2register()








