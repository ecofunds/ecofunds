from django.core.context_processors import csrf
from django.core.serializers import serialize
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils.simplejson import dumps, loads, JSONEncoder
from django.views.generic.list import ListView
from django.views.generic.detail import BaseDetailView
from django.views.generic import CreateView,DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.core.urlresolvers import reverse
from ecofunds.business import *
from ecofunds.models import Attachment
from ecofunds.user.models import UserProfile
from ecofunds.user.permissions import edit_allowance
from filetransfers.api import serve_file

class DjangoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, models.Model):
            #do the same as above by making it a queryset first
            set_obj = [obj]
            set_str = dumps(loads(serialize('json', set_obj)))
            #eliminate brackets in the beginning and the end 
            str_obj = set_str[1:len(set_str)-2]
            return str_obj

        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it
            return loads(serialize('json', obj))

        return JSONEncoder.default(self,obj)


class GlobalSuggestListView(ListView):
    context_object_name = 'list'
    http_method_names = ['post']
    template_name='project/suggest.html'

    def post(self, request, *args, **kwargs):
        max_items = 10
        data = {'suggestions': [], 'data': []}
        projects = ProjectData.suggestList(self.request.POST.get('search'), max_items)

        if projects.count < max_items:
            organizations = OrganizationData.suggestList(self.request.POST.get('search'), max_items - projects.count)

        for p in projects:
            data['suggestions'].append(p.title)
            data['data'].append(p)

        return http.HttpResponse(dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class SearchSuggestListView(ListView):
    context_object_name = 'list'
    http_method_names = ['get','post']
    template_name='search_suggest.html'   

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.method == "POST":
            data = self.request.POST
        else:
            data = self.request.GET

        
        sql = """
select b.* from (
	select 	'P' as result_type,
				p.entity_id as id,
				p.title as name,
				p.resume as description
	from		ecofunds_entities p
	where 	{fn concat(p.title, coalesce(p.acronym, ''))} like %s
	union all
	select 	'O',
				o.id,
				o.name,
				o.mission
	from		ecofunds_organization o
	where		{fn concat(o.name, coalesce(o.acronym, ''))} like %s
	union all
	select	'R',
				l.id,
				l.name,
				null
	from		ecofunds_locations l
	where		l.name like %s
) b order by 3
        
        """    
        search = data.get('search')
        if search:
            search = '%' + search + '%'
        else:
            search = '%'

        query_params = [search, search, search]

        cur = db.connection.cursor()
        cur.execute(sql, query_params)
        items = cur.fetchall()


        total =  len(items)
        results = []
        for x in items:

            if len(results) == 10:
                break

            url = ''
            onclick = ''
            if x[0] == 'P':
                url = 'project-detail'
            elif x[0] == 'O':
                url = 'organization-detail'
            else:
                onclick = 'fireSearch("' + x[2] + '")'
            results.append({'id': x[1], 'title':x[2], 'url': url, 'onclick' : onclick})
            

        self.object_list = results
        context = self.get_context_data(object_list=results)
        context.update({'len_list':  len(results)})
        context.update({'total':total})
        context.update(csrf(request))

        return self.render_to_response(context)


class FileDownload(BaseDetailView):

    def get(self, request, *args, **kwargs):

        id = self.kwargs.get('id')
        file = Attachment.objects.get(pk=id)
        return serve_file(request, file.path, None, True)

def item_permission_list(request,list):
    if request.user.is_authenticated(): 
        try:
            profile = request.user.get_profile()
        except UserProfile.DoesNotExist:
            profile = None
        if profile:
            contextlist = [[l,edit_allowance(l,profile)] for l in list]
            return contextlist
    contextlist = [[l,False] for l in list]
    return contextlist

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

class AttachmentCreateView(CreateView):
    model = Attachment

    template_name = 'attachments/attachment_form.html'

    def form_valid(self, form):
        self.object = form.save()
        f = self.request.FILES.get('file')
        data = [{'name': f.name, 'url': get_media_path(self.object,f.name), 'thumbnail_url': get_media_path(self.object,f.name), 
            'delete_url': reverse('upload-delete', args=[self.object.id]), 'delete_type': "DELETE"}]
        print data
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

class AttachmentDeleteView(DeleteView):
    model = Attachment

    def delete(self, request, *args, **kwargs):
        """
    This does not actually delete the file, only the database record. But
    that is easy to implement.
    """
        self.object = self.get_object()
        self.object.delete()
        if request.is_ajax():
            response = JSONResponse(True, {}, response_mimetype(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect('/upload/new')
            
class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = simplejson.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)


@csrf_exempt
def uploadify_upload(request):
    if request.method == 'POST':
        upload = request.FILES['Filedata']
        try:
            dest = open('../static/media/'+upload.name,"wb+")
            for block in upload.chunks():
                dest.write(block)
            dest.close()
        except IOError:
            pass
        response = HttpResponse()
        response.write("%s\r\n"%upload.name)
        return response
