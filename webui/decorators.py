from django.http import HttpResponse
from datetime import datetime
import pytz
import uuid
from models import UserToken

def auth_token(function=None, rate_limit=None):
    def decorator(view_func):
        def decorated(request, *args, **kwargs):

            try:
                token = request.META['HTTP_X_AUTHTOKEN']
            
                uuid.UUID(token)
                usertoken = UserToken.objects.get(token=token)

                if usertoken.expires < datetime.now(pytz.utc):
                    return HttpResponse(status=403)                    

                # Do rate limit check here
                

            except Exception as e:
                print str(e)
                return HttpResponse(status=403)

            response = view_func(request, *args, usertoken=usertoken, **kwargs)
            
            return response
            
        decorated.__name__ = view_func.__name__
        decorated.__dict__ = view_func.__dict__
        decorated.__doc__ = view_func.__doc__

        return decorated
        
    if function is None:
        return decorator
    else:
        return decorator(function)
