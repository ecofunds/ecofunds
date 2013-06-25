from django import http
from django.core.cache import cache
from django.core.context_processors import csrf
from django.utils.simplejson import dumps
from django.db import models
from django.db.models import Count
from django.utils.functional import curry
from django.views.generic.list import ListView
from django.views.generic.detail import BaseDetailView
from django.utils.translation import ugettext_lazy as _

from ecofunds.views import DjangoJSONEncoder
from ecofunds.business import *
from ecofunds.maps import *
from ecofunds.maps.models import GoogleMapView
from ecofunds.models import Project

from gmapi import maps
from babel import numbers
from BeautifulSoup import BeautifulSoup

import colorsys
import math
import pylab
import xlwt


from pygeoip import GeoIP

from django import db

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

class ProjectChartSourceView(BaseDetailView):
    def get(self, request, *args, **kwargs):

        if request.method == "POST":
            data = request.POST
        else:
            data = request.GET

        result = [['Country', 'Projects']]

        list = ProjectData.list(order_by='projects_locations__location__country__name', projects_locations__location__country_id__gt=0).values('projects_locations__location__country__name').annotate(total=Count('entity_id'))
        
        for item in list:
            result.append([item['projects_locations__location__country__name'], item['total']])

        return http.HttpResponse(dumps(result, cls=DjangoJSONEncoder), content_type='application/json')

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class ProjectMapSourceView(GoogleMapView, BaseDetailView):
    def get(self, request, *args, **kwargs):
        db.reset_queries()
        if request.method == "POST":
            data = request.POST
        else:
            data = request.GET

        view = 'heat'
        center = None
        zoom = 4
        mapTypeId = None

        if data.has_key('view'):
            view = data.get('view')


        if data.has_key('concentration'):
            view = 'concentration'
        if data.has_key('center'):
            c = data.get('center').split(',')
            center = maps.LatLng(c[0], c[1])
        if data.has_key('zoom'):
            zoom = int(data.get('zoom'))
        if data.has_key('mapTypeId'):
            mapTypeId = data.get('mapTypeId')
        print "Center ", center
        gmap = self.get_map(request, center, zoom, mapTypeId)


        sql_columns = """a.location_id, 
			a.entity_id,
			count(b.entity_id),
			d.polygon
            """
        if view == 'concentration':
            sql_columns = "	min(c.amount_usd), max(c.amount_usd) "

        sql = "SELECT 	" + sql_columns + """
FROM ecofunds_entity_locations a
INNER JOIN ecofunds_entities  b ON (a.entity_id = b.entity_id) 
INNER JOIN ecofunds_investments c ON  c.recipient_entity_id = b.entity_id
INNER JOIN ecofunds_locations d ON d.id = a.location_id
inner join ecofunds_countries cou on cou.id = d.country_id
WHERE b.validated = 1
"""

        query_params = []
        if data.has_key('s_project_name') and data['s_project_name'] != '':
            sql+=" and b.title like %s "
            query_params.append('%' + data['s_project_name'] + '%')
        if data.has_key('s_project_activity_type') and data['s_project_activity_type']!='':
            sql+=" and exists (select 1 from ecofunds_entity_activities e where e.entity_id = b.entity_id and e.activity_id = %s) "
            query_params.append(data['s_project_activity_type'])

        if data.has_key('s_organization') and data['s_organization'] != '':
            sql+=' and exists (select 1 from ecofunds_organization f where f.id in (c.recipient_organization_id, c.funding_organization_id) and {fn concat(f.name, f.acronym)} like %s) '
            query_params.append('%' + data['s_organization'] + '%')

        
        if data.has_key('s_country') and data['s_country'] != '':
            sql+=" and cou.name like %s "
            query_params.append('%'+data['s_country'] + '%')

        if data.has_key('s_state') and data['s_state'] != '':
            sql+=" and (d.iso_sub = %s or d.name like %s) "
            query_params.append(data['s_state'])
            query_params.append('%'+data['s_state']+'%')
        


        
        s_grant_from = trans_date(data.get('s_date_from'))
        s_grant_to = trans_date(data.get('s_date_to'))

        if s_grant_from:
            sql+=" and b.grant_from >= %s "
            query_params.append(s_grant_from)
        if s_grant_to:
            sql+=" and b.grant_to <= %s "
            query_params.append(s_grant_to)
        
        min_invest = 0
        max_invest = 99999999
        if data.has_key('s_investments_from') and data['s_investments_from'] != '':
            min_invest = float(data['s_investments_from'])
        if data.has_key('s_investments_to') and data['s_investments_to']:
            max_invest = float(data['s_investments_to'])
        if max_invest == 0:
            max_invest = 99999999
        if min_invest > max_invest:
            min_invest, max_invest = max_invest, min_invest
        if min_invest > 0 or max_invest < 99999999:
            sql+= ' and b.budget between %s and %s '
            query_params.append(min_invest)
            query_params.append(max_invest)

        if view != 'concentration':
            sql+=" group by a.location_id "

        cursor = db.connection.cursor()
        cursor.execute(sql, query_params)
       
        #list = ProjectData.locationFilteredList(request)
        points = {}
            
        if view == 'concentration':
            start, end = 0, 0
            for item in cursor.fetchall():
                if not (item[0] is None):
                    start = float(item[0])
                    end = float(item[1])
            json = {'start': format_currency(start), 'end': format_currency(end)}            

            return http.HttpResponse(dumps(json, cls=DjangoJSONEncoder), content_type='application/json')
        

        for item in cursor.fetchall():
            location_id = item[0]
            entity_id = item[1]
            amount = item[2]
            xml = BeautifulSoup(item[3])

            key = 'pos'+str(location_id)            

            if not points.has_key(key):
                paths = []
                
                for polygon in xml.findAll('polygon'):
                    corners = []
                    latlngs = []
                    coordinates = polygon.outerboundaryis.linearring.coordinates.text.split(' ')
                    
                    for c in coordinates:
                        
                        o = c.split(',')
                        cx = float(o[1])
                        cy = float(o[0])
                        corners.append((cx, cy))
                        latlngs.append(maps.LatLng(cx, cy))

                    x, y = self.polygon_centroid(corners)
                    paths.append(latlngs)

                    
                points[key] = {'centroid': maps.LatLng(x, y), 'paths': paths, 'investment': 0, 'projects': [{'id': entity_id, 'amount': amount}]}
            else:
                b = False
                for p in points[key]['projects']:
                    if p['id'] == entity_id:
                        b = True
                if not b:
                    points[key]['projects'].append({'id': entity_id, 'amount': amount})

        for key in points:
            for o in points[key]['projects']:
                points[key]['investment'] += o['amount']

        if len(points) > 0:
            sum_inv = sum(points[key]['investment'] for key in points)
            max_inv = max(points[key]['investment'] for key in points)
            min_inv = min(points[key]['investment'] for key in points)

            if view == 'bubble':

                for key in points:
                    amount = points[key]['investment']
                    scale = 5 * int(math.floor(((amount-min_inv)/(max_inv-min_inv))*10)+1)

                    marker = maps.Marker(opts = {
                        'map': gmap,
                        'position': points[key]['centroid'],
                        'icon': {
                            'path': SymbolPath.CIRCLE,
                            'fillOpacity': 0.7,
                            'fillColor': '#FFFFFF',
                            'strokeOpacity': 1.0,
                            'strokeColor': '#00539f',
                            'strokeWeight': 1, 
                            'scale': scale
                        }
                    })

                    #t = loader.get_template('maps/info-bubble.html')
                    #c = Context({ 'org': org })
                
                    info = InfoBubble({
                        'content': 'teste',#t.render(c),
                        'disableAutoPan': True,
                        'backgroundColor': '#FFF',
                        'borderRadius': 10,
                        'borderWidth': 0,
                        'padding': 0,
                        'minHeight': 40,
                        'minWidth': 400,
                        'maxWidth': 400,
                        'shadowStyle': 1,
                        'arrowPosition':10,
                        'hideCloseButton': True,
                    })
                    info.open(gmap, marker)

            elif view == 'density':
            
                for key in points:
                    amount = points[key]['investment']
                    #text = numbers.format_currency(
                    #        float(amount),
                    #        numbers.get_currency_symbol('USD', 'en_US'),
                    #        u'\xa4\xa4 #,##0.00', locale=request.LANGUAGE_CODE.replace('-', '_')
                    #    )

                    text = "  " +  str(amount) + "  "

                    scale = (len(text)+1) * 3

                    marker = maps.Marker(opts = {
                        'map': gmap,
                        'position': points[key]['centroid'],
                        'icon': {
                            'path': SymbolPath.CIRCLE,
                            'fillOpacity': 0.8,
                            'fillColor': '#8eb737',
                            'strokeWeight': 0, 
                            'scale': scale
                        }
                    })

                    label = Label(opts={
                        'map': gmap,
                        'position': points[key]['centroid'],
                        'text': text
                    })

            elif view == 'heat':

                fill_colors = ['#28B9D4', '#7CC22C', '#ECCE0A', '#ED8A09', '#ED0B0C']
                for key in points:
                    amount = points[key]['investment']
                    #scale = int(math.floor((((amount-min_inv)/(max_inv-min_inv))*10)/2)-1)
                    if min_inv == max_inv:
                        scale = 1.0
                    else:
                        scale = round( float(amount-min_inv)/float(max_inv-min_inv), 2)

                    tp = pylab.cm.RdYlGn(1 - scale)
                    rgb = []
                    for c in tp[:3]:
                        rgb.append(c * 255)

                    h = '#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2])

                    polygon = maps.Polygon(opts = {
                        'map': gmap,
                        'paths': points[key]['paths'],
                        'strokeWeight': 0.8,
                        'strokeColor': h,
                        'fillColor':  h,
                        'fillOpacity': 0.5
                    })
                    maps.event.addListener(polygon, 'mouseover', 'ecofundsMap.polygonOver')
                    maps.event.addListener(polygon, 'mouseout', 'ecofundsMap.polygonOut')


        

        return http.HttpResponse(dumps(gmap, cls=DjangoJSONEncoder), content_type='application/json')

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

        
        geo = GeoIP("geoip/GeoLiteCity.dat")
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
