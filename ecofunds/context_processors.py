
from django.utils.translation import get_language
from django.conf import settings

def user(request):
    lang = get_language()
    # FIXME: Learn the impact and remove the next 2 lines.
    date_format = settings.DATE_FORMAT
    number_format = 'decimal-us'
    
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
