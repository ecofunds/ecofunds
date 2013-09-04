import logging

from django import http
from django.core.context_processors import csrf
from django.utils.simplejson import dumps
from django.views.generic.list import ListView

from ecofunds.core.models import Organization
from ecofunds.core.views import DjangoJSONEncoder


log = logging.getLogger(__name__)

class OrganizationSuggestListView(ListView):
    context_object_name = 'list'
    http_method_names = ['post']
    template_name='organization/suggest.html'
    data_type = "json"

    def post(self, request, *args, **kwargs):
        data = {'suggestions': [], 'data': []}
        search = request.POST.get('search')
        qty = request.POST.get('limit')
        if qty == None:
            qty = 10
        #self.object_list = OrganizationData.list('name', name__icontains=search)[:qty]

        self.object_list = Organization.objects.raw('select * from ecofunds_organization where {fn concat(name, acronym)} like %s order by name', ['%'+search+'%'])[:5]

        if self.data_type == "html":
            context = self.get_context_data(object_list=self.object_list)
            context.update(csrf(request))
            return self.render_to_response(context)

        for p in list:
            data['suggestions'].append(p.title)
            data['data'].append(p)

        return http.HttpResponse(dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
