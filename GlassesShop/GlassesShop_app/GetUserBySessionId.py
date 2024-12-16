from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
import redis

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def getUserBySessionId(request):
    ssid = request.COOKIES.get('session_id')
    if ssid:
        try:
            email = session_storage.get(ssid).decode('utf-8')
            user = get_user_model().objects.get(email=email)
        except AttributeError:
            user = AnonymousUser()
    else:
        user = AnonymousUser() 
    return user