import logging
import math
import time

from django import db
from django import http
from django.core.cache import cache
from django.core.context_processors import csrf
from django.utils.simplejson import dumps, loads
from django.db import models
from django.db.models import Count
from django.utils.functional import curry
from django.views.generic.list import ListView
from django.views.generic.detail import BaseDetailView
from django.utils.translation import ugettext_lazy as _

from ecofunds.core.models import Project
from ecofunds.core.views import DjangoJSONEncoder
from ecofunds.business import *
from ecofunds.maps import *
from ecofunds.maps.models import GoogleMapView
from ecofunds.colors_RdYlGn import scale as color_scale

import xlwt

from babel import numbers
from BeautifulSoup import BeautifulSoup
from pygeoip import GeoIP

log = logging.getLogger(__name__)

class ProjectFilteredListExcel(BaseDetailView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        list = ProjectData.filteredList(request, 0)

        response = http.HttpResponse(mimetype="application/ms-excel") #application/vnd.ms-excel
        response['Content-Disposition'] = 'attachment; filename=projects.xls'

        w = xlwt.Workbook(encoding="UTF-8")
        ws = w.add_sheet('Projects')

        headerBorders = xlwt.Borders()
        headerBorders.left = 2
        headerBorders.right = 2
        headerBorders.top = 2
        headerBorders.bottom = 2

        headerFont = xlwt.Font()
        headerFont.name = 'Arial'
        headerFont.colour_index = 4
        headerFont.bold = True

        headerStyle = xlwt.XFStyle()
        headerStyle.font = headerFont
        headerStyle.borders = headerBorders

        rowBorders = xlwt.Borders()
        rowBorders.left = 1
        rowBorders.right = 1
        rowBorders.top = 1
        rowBorders.bottom = 1

        rowFont = xlwt.Font()
        rowFont.name = 'Arial'

        dateStyle = xlwt.XFStyle()
        dateStyle.num_format_str = "D/MMM/YY"
        dateStyle.font = rowFont
        dateStyle.borders = rowBorders

        floatStyle = xlwt.XFStyle()
        floatStyle.num_format_str = '"$"#,##0.00_);("$"#,##'
        floatStyle.font = rowFont
        floatStyle.borders = rowBorders

        rowStyle = xlwt.XFStyle()
        rowStyle.font = rowFont
        rowStyle.borders = rowBorders

        ws.col(0).width = 0x0d00 * 8
        ws.col(1).width = 0x0d00 * 1.5
        ws.col(2).width = 0x0d00 * 1.5
        ws.col(3).width = 0x0d00 * 2

        ws.write(0, 0, unicode(_('Name')), headerStyle)
        ws.write(0, 1, unicode(_('Completion date')), headerStyle)
        ws.write(0, 2, unicode(_('Received total (U$)')), headerStyle)
        ws.write(0, 3, unicode(_('Region')), headerStyle)

        i = 1
        for project in list:
            year_amount = sum(project.get_year_recipient_investments()) if project.get_year_recipient_investments().count > 0 else 0
            p_location = project.get_firstlocation()

            ws.write(i, 0, project.title, rowStyle)
            ws.write(i, 1, project.grant_to, dateStyle)
            ws.write(i, 2, year_amount, floatStyle)
            ws.write(i, 3, p_location.location.name if p_location else '', rowStyle)
            i+=1
        w.save(response)

        return response

class ProjectSuggestListView(ListView):
    context_object_name = 'list'
    http_method_names = ['get','post']
    template_name='project/suggest.html'
    data_type = "json"

    def get_queryset(self, quantity):
        if self.request.method == "POST":
            data = self.request.POST
        else:
            data = self.request.GET

        return ProjectData.suggestList(data.get('search'), quantity )

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {'suggestions': [], 'data': []}
        self.object_list = self.get_queryset(request.POST['limit'])

        if self.data_type == "html":
            context = self.get_context_data(object_list=self.object_list)
            context.update(csrf(request))
            return self.render_to_response(context)

        for p in list:
            data['suggestions'].append(p.title)
            data['data'].append(p)

        return http.HttpResponse(dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

class ProjectListView(ListView):
    context_object_name = 'list'
    http_method_names = ['get', 'post']

    def get_queryset(self):

        limit = 9

        if self.request.method == "POST":
            data = self.request.POST
        else:
            data = self.request.GET

        if data.has_key('limit'):
            limit = data.get('limit')

        list, self.form, self.labels = ProjectData.filteredList(self.request, limit)

        return list

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})
        context = self.get_context_data(object_list=self.object_list)
        context.update({'form': self.form})
        context.update(csrf(request))

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

class CountriesSuggestListView(ListView):
    context_object_name = 'list'
    http_method_names = ['post']
    template_name='project/countries.html'
    data_type = "json"

    def post(self, request, *args, **kwargs):
        data = {'suggestions': [], 'data': []}
        search = request.POST.get('search')
        qty = request.POST.get('limit')
        if qty == None:
            qty = 10
        self.object_list = Country.objects.filter(name__icontains=search).order_by('name')#[:qty]

        if self.data_type == "html":
            context = self.get_context_data(object_list=self.object_list)
            context.update(csrf(request))
            return self.render_to_response(context)

        for p in list:
            data['suggestions'].append(p.title)
            data['data'].append(p)

        return http.HttpResponse(dumps(data, cls=DjangoJSONEncoder), content_type='application/json')




class RegionsSuggestListView(ListView):
    context_object_name = 'list'
    http_method_names = ['post']
    template_name='project/countries.html'
    data_type = "json"

    def post(self, request, *args, **kwargs):
        data = {'suggestions': [], 'data': []}
        search = request.POST.get('search')
        qty = request.POST.get('limit')
        if qty == None:
            qty = 10


        self.object_list = Location.objects.filter(name__icontains=search).order_by('name')[:qty]

        if self.data_type == "html":
            context = self.get_context_data(object_list=self.object_list)
            context.update(csrf(request))
            return self.render_to_response(context)

        for p in list:
            data['suggestions'].append(p.title)
            data['data'].append(p)

        return http.HttpResponse(dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class GeoIpView(ListView):
    def get(self, request, *args, **kwargs):
        ip = request.META.get('X-FORWARDED-FOR')
        if not ip:
            ip = request.META['REMOTE_ADDR']



        if ip[:3] == "127" or ip[:8] == "168.192." or ip[:10] == "192.168.0.":
            ip = "201.76.161.146"


        from django.conf import settings
        geo = GeoIP(settings.GEOIP_DATABASE)
        region = geo.record_by_addr(ip)


        return http.HttpResponse(dumps(region, cls=DjangoJSONEncoder), content_type='application/json')

def remove_project(request):
    id = request.GET['id']
    try:
        proj = Project.objects.get(pk=id)
    except Project.DoesNotExist:
        data = {'status':False}
        return http.HttpResponse(dumps(data,cls=DjangoJSONEncoder),content_type='application/json')
    proj.active=False
    proj.save()
    data = {'status':True}
    return http.HttpResponse(dumps(data,cls=DjangoJSONEncoder),content_type='application/json')
