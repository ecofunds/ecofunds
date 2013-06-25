from django import http
from django.core.cache import cache
from django.utils import simplejson as json
from django.views.generic.detail import BaseDetailView
from django.utils.html import escape

class SourceView(BaseDetailView):

    def get(self, request, *args, **kwargs):
        gmap = cache.get('gmap_%s' % self.kwargs['slug'])
        return self.get_json_response(gmap)

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)

    def render_to_response(self, context):
        return self.get_json_response(json.dumps(cache.get('gmap_%s' % self.kwargs['slug']), separators=(',', ':')))