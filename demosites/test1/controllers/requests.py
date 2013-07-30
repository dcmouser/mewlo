# requests.py
# This file holds controller functions that will be invoked by route manager







def request_home(request):
    request.response.set_responsedata("In request_home.")
    return (True,"")



def request_about(request):
    request.response.set_responsedata("In request_about.")
    return (True,"")



def request_sayhello(request):
    matchedroute = request.get_matchedroute()
    args = request.get_route_parsedargs()
    extra = matchedroute.get_extra()
    request.response.set_responsedata("In request_sayhello, with args: "+str(args)+" and extra: "+str(extra))
    return (True,"")



def request_article(request):
    request.response.set_responsedata("In request_article.")
    return (True,"")




# test
class request_test_class(object):
    def __init__(self):
        pass
    @classmethod
    def testinvoke(cls,request):
        request.response.set_responsedata("In request_test_class invoke().")
        return (True,"")