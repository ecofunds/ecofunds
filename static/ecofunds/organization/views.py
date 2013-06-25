from django import http
from django.core.cache import cache
from django.core.context_processors import csrf
from django.utils.simplejson import dumps
from django.db import models
from django.db.models import Count
from django.template import loader, Context
from django.utils.functional import curry
from django.views.generic.list import ListView
from django.views.generic.detail import BaseDetailView

from ecofunds.views import DjangoJSONEncoder
from ecofunds.business import *
from ecofunds.maps import *
from ecofunds.maps.models import GoogleMapView
from ecofunds.models import Organization

from gmapi import maps
from babel import numbers
from BeautifulSoup import BeautifulSoup

import colorsys
import math

import pylab

from django import db

class OrganizationChartSourceView(BaseDetailView):
    def get(self, request, *args, **kwargs):

        if request.method == "POST":
            data = request.POST
        else:
            data = request.GET

        result = [['Country', 'Organizations']]

        list = OrganizationData.list(order_by='country__name', country_id__gt=0).values('country__name').annotate(total=Count('id'))
        
        for item in list:
            result.append([item['country__name'], item['total']])

        return http.HttpResponse(dumps(result, cls=DjangoJSONEncoder), content_type='application/json')

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

class OrganizationMapSourceView(GoogleMapView, BaseDetailView):
    def get(self, request, *args, **kwargs):
        if settings.DEBUG:
            db.reset_queries()
        if request.method == "POST":
            data = request.POST
        else:
            data = request.GET

        center = None
        zoom = 4
        mapTypeId = None

        if data.has_key('center'):
            c = data.get('center').split(',')
            center = maps.LatLng(c[0], c[1])

        if data.has_key('zoom'):
            zoom = int(data.get('zoom'))

        if data.has_key('mapTypeId'):
            mapTypeId = data.get('mapTypeId')

        gmap = self.get_map(request, center, zoom, mapTypeId)

#        list = OrganizationData.filteredList(request, 0, desired_location_lat__isnull=False, desired_location_lng__isnull=False)
        
#       for item in list:
#           print 1

        
        markers = []

        t = loader.get_template('maps/info-bubble.html')
        
        sql = """
select 		    o.name, 
		        o.desired_location_lat, 
		        o.desired_location_lng
from	        ecofunds_organization o
where			desired_location_lat is not null and desired_location_lng is not null
"""
        query_params = []

        if data.has_key('s_organization') and data['s_organization'] != '':
            sql += " and {fn concat(o.name, o.acronym)} like %s "
            query_params.append('%' + data['s_organization'] + '%')

        if data.has_key('s_organization_type') and data['s_organization_type'] != '':
            sql += " and o.type_id = %s "
            query_params.append('%' + data['s_organization_type'] + '%')
        

        if data.has_key('s_country') and data['s_country'] != '':
            sql+=" and cou.name like %s "
            query_params.append('%'+data['s_country'] + '%')

        if data.has_key('s_state') and data['s_state'] != '':
            sql+=" and o.state = %s "
            query_params.append(data['s_state'])


        dt_from = trans_date(data['s_investment_date_from'])
        dt_to = trans_date(data['s_investment_date_to'])
        
        if dt_from or dt_to:
            sql+= " and exists (select 1 from ecofunds_investments where o.id in (recipient_organization_id, funding_organization_id) "
            if dt_from:
                sql+= " and created_at >= %s "
                query_params.append(dt_from)
            if dt_to:
                sql+= " and created_at <= %s "
                query_params.append(dt_to)
      
            sql+= ") "
        if data.has_key('s_investments_focus') and data['s_investments_focus'] != '':
            sql+=""" and exists (select 1 from ecofunds_entity_organizations eo
inner join ecofunds_entity_activities ea on ea.entity_id = eo.entity_id
where eo.organization_id = o.id and ea.activity_id = %s) """
            query_params.append(data['s_investments_focus'])

        

        sql += """
        group by 	    o.name, 
				o.desired_location_lat, 
				o.desired_location_lat

        """
        min_invest = 0
        max_invest = 99999999
        if data.has_key('s_estimated_investments_value_from') and data['s_estimated_investments_value_from'] != '':
            min_invest = float(data['s_estimated_investments_value_from'])
        if data.has_key('s_estimated_investments_value_to') and data['s_estimated_investments_value_to']:
            max_invest = float(data['s_estimated_investments_value_to'])
        if max_invest == 0:
            max_invest = 99999999
        if min_invest > max_invest:
            min_invest, max_invest = max_invest, min_invest
        if min_invest > 0 or max_invest < 99999999:
            sql+=" having sum(i.amount_usd) between %s and %s "
            query_params.append(min_invest)
            query_params.append(max_invest)

        

        cursor = db.connection.cursor()
        cursor.execute(sql, query_params) 

        for org in cursor.fetchall():

            item = Organization()
            item.name = org[0]
            item.desired_location_lat = org[1]
            item.desired_location_lng = org[2]


            marker = maps.Marker(opts = {
                'map': gmap,
                'position': maps.LatLng(item.desired_location_lat, item.desired_location_lng),
                'icon': maps.MarkerImage('http://maps.google.com/mapfiles/marker_white.png')
            })

            maps.event.addListener(marker, 'click', 'ecofundsMap.markerClick')

            c = Context({ 'org': item })
            info = InfoBubble({
                'content': t.render(c),
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
            markers.append(marker)

        clusterer = MarkerClusterer(gmap, markers, opts = {'gridSize': 30, 'maxZoom':14})



        return http.HttpResponse(dumps(gmap, cls=DjangoJSONEncoder), content_type='application/json')


    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)




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


def remove_organization(request):
    id = request.GET['id']
    try:
        org = Organization.objects.get(pk=id)
    except Organization.DoesNotExist:
        data = {'status':False}
        return http.HttpResponse(dumps(data,cls=DjangoJSONEncoder),content_type='application/json')
    org.active=False
    org.save()
    data = {'status':True}
    return http.HttpResponse(dumps(data,cls=DjangoJSONEncoder),content_type='application/json')
