
from django.utils.translation import get_language
from ecofunds import settings

def user(request):
    lang = get_language()
    date_format = settings.LANGUAGES_DATEFORMAT[lang]
    number_format = settings.LANGUAGES_NUMBERFORMAT[lang]
    
    if hasattr(request,'user'):
        try:
            profile = request.user.get_profile()
        except:
            profile =None
        return {'user':request.user,
                'profile':profile,
                'date_format':date_format,
                'number_format': number_format}
    return {}
