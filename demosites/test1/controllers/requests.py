# requests.py
# This file holds controller functions that will be invoked by route manager







def request_home(request):
    request.response.set_responsedata("In request_home.")
    return (True,"")



def request_about(request):
    request.response.set_responsedata("In request_about.")
    return (True,"")



def request_sayhello(request):
    request.response.set_responsedata("In request_sayhello.")
    return (True,"")



def request_article(request):
    request.response.set_responsedata("In request_article.")
    return (True,"")
