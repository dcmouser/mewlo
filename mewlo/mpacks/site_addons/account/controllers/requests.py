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
    #return lhelper.handlepage_register_deferred()
    return lhelper.handlepage_register_immediate()



def request_deferred_verify(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_verify_registration_deferred()






def request_profile(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_profile()





def request_userfield_verify(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_verify_userfield()














def resend_register_verification(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_resend_register_verification()


def reset_password(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_reset_password()


def modify_field(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_modify_field()

def modify_field_confirmation(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_modify_field_confirmation()


def login_bycode(request, response):
    """Controller function."""
    # account helper
    lhelper = AccountHelper(request, response)
    # then page contents
    return lhelper.handlepage_login_bycode()

