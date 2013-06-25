from cms.middleware.multilingual import MultilingualURLMiddleware 
from cms.utils.i18n import get_default_language

from django.http import HttpResponseRedirect
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.conf import settings

import re

SUPPORTED = dict(settings.CMS_LANGUAGES)
START_SUB = re.compile(r"^/(%s)/.*" % "|".join(map(lambda l: l[0], settings.CMS_LANGUAGES)))

def has_lang_prefix(path):
    check = START_SUB.match(path)
    if check is not None:
        return check.group(1)
    else:
        return False

class CustomMultilingualURLMiddleware(MultilingualURLMiddleware):

    def process_request(self, request):
        
        lang_path = request.path.split('/')[1]
        if lang_path in settings.URLS_WITHOUT_LANGUAGE_REDIRECT:
            return None

        rlang = self.get_language_from_request(request)

        if hasattr(request, "session"):
            lang = request.session.get("django_language", None)
        elif "django_language" in request.COOKIES.keys():
            lang = request.COOKIES.get("django_language", None)
        
        if (lang not in SUPPORTED or lang is None):# and (rlang is not None and rlang != ""):
            lang = rlang
        #else:
        #    lang = settings.CMS_LANGUAGES[0][0]

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        #if lang_path == '': 
        #    return HttpResponseRedirect('/%s/' % lang)
        #if len([z for z in settings.LANGUAGES if z[0] == lang_path]) == 0:
        #    return HttpResponseRedirect('/%s%s' % (lang, request.path))

    def process_response(self, request, response):
        
        prefix = has_lang_prefix(request.path_info)
        if prefix:
            request.path = "/" + "/".join(request.path.split("/")[2:])
            request.path_info = "/" + "/".join(request.path_info.split("/")[2:]) 
            t = prefix
            if t in SUPPORTED:
                lang = t
                
                if hasattr(request, "session"):
                    request.session["django_language"] = lang
                else:
                    response.set_cookie("django_language", lang)

        return response