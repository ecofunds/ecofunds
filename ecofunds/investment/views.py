from django import http
from django.core.cache import cache
from django.db.models import Count
from django.utils.simplejson import dumps
from django.views.generic.detail import BaseDetailView
from ecofunds.business import ProjectData, OrganizationData, InvestmentData
from ecofunds.views import DjangoJSONEncoder
from collections import Counter
from django import db
from ecofunds.maps.models import GoogleMapView
from ecofunds.models import Investment
from BeautifulSoup import BeautifulSoup
from gmapi import maps
from babel import numbers


import colorsys
import math
import pylab
import sys
sys.setrecursionlimit(10000)

from gmapi.maps import MapConstantClass, MapClass, Args

SymbolPath = MapConstantClass('SymbolPath', ('CIRCLE',))

def format_currency(value):
    return numbers.format_currency(
            float(value),
            numbers.get_currency_symbol('USD', 'en_US'),
            u'\xa4\xa4 #,##0.00', locale='pt_BR')

class Circle(MapClass):

    _getopts = {

    }
    _setopts = {
        'setMap': 'map',
    }

    def __init__(self, opts=None):
        super(Circle, self).__init__(cls='Circle')
        self._map = None
        self['arg'] = Args(['opts'])
        self.setOptions(opts)

    def __unicode__(self):
        opts = self['arg'].get('opts', {})
        params = []
        if 'strokeColor' in opts:
            color = 'color:0x%s' % opts['strokeColor'].lstrip('#').lower()
            if 'strokeOpacity' in opts:
                color += '%02x' % min(max(opts['strokeOpacity'] * 255, 0), 255)
            params.append(color)
        if 'strokeWeight' in opts:
            params.append('weight:%d' % opts['strokeWeight'])
        return '|'.join(params)

    def getMap(self):
        return self._map

    def setOptions(self, options):
        if options and 'map' in options:
            if self._map:
                # Remove this polyline from the map.
                self._map['crl'].remove(self)
            # Save new map reference.
            self._map = options.pop('map')
            if self._map:
                self._map.setdefault('crl', []).append(self)

        super(Circle, self).setOptions(options)


class Label(MapClass):

    def __init__(self, opts=None):
        super(Label, self).__init__(cls='Label', context='')
        self._map = None
        self['arg'] = Args(['opts'])

        self.setOptions(opts)

    def __unicode__(self):
        opts = self['arg'].get('opts', {})
        params = []
        return '|'.join(params)

    def getMap(self):
        return self._map

    def setOptions(self, options):
        if options and 'map' in options:
            self._map = options.pop('map')
        if self._map:
            self._map.setdefault('lbl', []).append(self)

        super(Label, self).setOptions(options)

class MarkerClusterer(MapClass):
    _getopts = {
        'getMarkers': 'markers',
    }
    _setopts = {
        'setMarkers': 'markers',
    }

    def __init__(self, map, markers, opts=None):
        super(MarkerClusterer, self).__init__(cls='MarkerClusterer', context='', mapIntoConstructor=True)
        self._map = map
        self['arg'] = Args(['map', 'markers', 'opts'])

        if map:
            self['arg'].setdefault('map', {})
        if markers:
            self['arg'].setdefault('markers', [])

        self.setOptions(opts)

    def __unicode__(self):
        opts = self['arg'].get('opts', {})
        params = []
        return '|'.join(params)

    def getMap(self):
        return self._map

    def setOptions(self, options):
        if options and 'map' in options:
            self._map = options.pop('map')
        if self._map:
            self._map.setdefault('mkc', []).append(self)

        super(MarkerClusterer, self).setOptions(options)

class InfoBubble(MapClass):
    _getopts = {
        'getContent': 'content',
        'getPosition': 'position',
        'getShadowStyle': 'shadowStyle',
        'getPadding': 'padding',
        'getBackgroundColor': 'backgroundColor',
        'getBorderRadius': 'borderRadius',
        'getArrowSize': 'arrowSize',
        'getBorderWidth': 'borderWidth',
        'getBorderColor': 'borderColor',
        'getDisableAutoPan': 'disableAutoPan',
        'getHideCloseButton': 'hideCloseButton',
        'getArrowPosition': 'arrowPosition',
        'getArrowDirection': 'arrowDirection',
        'getBackgroundClassName': 'backgroundClassName',
        'getArrowStyle': 'arrowStyle'
    }
    _setopts = {
        'setContent': 'content',
        'setPosition': 'position',
        'setShadowStyle': 'shadowStyle',
        'setPadding': 'padding',
        'setBackgroundColor': 'backgroundColor',
        'setBorderRadius': 'borderRadius',
        'setArrowSize': 'arrowSize',
        'setBorderWidth': 'borderWidth',
        'setBorderColor': 'borderColor',
        'setDisableAutoPan': 'disableAutoPan',
        'setHideCloseButton': 'hideCloseButton',
        'setArrowPosition': 'arrowPosition',
        'setArrowDirection': 'arrowDirection',
        'setBackgroundClassName': 'backgroundClassName',
        'setArrowStyle': 'arrowStyle'
    }

    def __init__(self, opts=None):
        super(InfoBubble, self).__init__(cls='InfoBubble', context='')
        self._map = None
        self['arg'] = Args(['opts'])
        self.setOptions(opts)

    def open(self, map, anchor=None):
        if anchor:
            anchor.setMap(map)
            anchor['nfo'] = self
        else:
            map['nfo'] = self








def trans_date(v):
    v = str(v)
    if len(v)==10:
        tup = v.split('/')
        print int(tup[2])
        if int(tup[2]) < 1900:
            return ''

        v = tup[2] + '-'+tup[1] + '-' + tup[0]
        return v
    else:
        return ''
    
SymbolPath = MapConstantClass('SymbolPath',
                             ('CIRCLE',))

class InvestmentFlowSource(BaseDetailView):

    def dict2obj(self, d):
        if isinstance(d, list):
            d = [self.dict2obj(x) for x in d]
        if not isinstance(d, dict):
            return d
        class C(object):
            pass
        o = C()
        for k in d:
            o.__dict__[k] = self.dict2obj(d[k])
        return o

    def __init__(self, **kwargs):
        super(InvestmentFlowSource, self).__init__(**kwargs)

        self.before_investments = []
        self.after_investments = []

        self.before_orgs = []
        self.before_projects = []

        self.after_orgs = []
        self.after_projects = []

    def before_flow(self, investment, childrens, level=1):
        
        investment = self.dict2obj(investment)
        self.before_investments.append(investment.id)
        # Financiadores
        if investment.funding_entity:
            funding = ProjectData.item(investment.funding_entity)
                
            investments = InvestmentData.list(recipient_entity_id=funding.entity_id).exclude(pk__in=self.before_investments, created_at__gt=investment.created_at).all().values('id', 'created_at', 'funding_entity', 'funding_organization').annotate(projects=Count('funding_entity'), organizations=Count('funding_organization'))
            #investments = funding.recipient_investments.all()
            
            obj = {'id': 'p_%d_%d' % (level, funding.entity_id), 'name': funding.title, 'data': {'level': level, 'css': 'project', 'count': len(investments)}, 'children': [] }
            childrens.append(obj)

            self.before_projects.append(funding.entity_id)
            c = Counter(self.before_projects)
            
            if len(investments) > 0 and c[funding.entity_id] < 2:
                for inv in investments:
                    self.before_flow(inv, obj['children'], level+1)

        elif investment.funding_organization:
            funding = OrganizationData.item(investment.funding_organization)

            investments = InvestmentData.list(recipient_organization_id=funding.id).exclude(pk__in=self.before_investments, created_at__gt=investment.created_at).all().values('id', 'created_at', 'funding_entity', 'funding_organization').annotate(projects=Count('funding_entity'), organizations=Count('funding_organization'))
            #investments = funding.recipient_investments.all()
            print(investments)
            obj = {'id': 'o_%d_%d' % (level, funding.id), 'name': funding.name, 'data': {'level': level, 'css': 'organization', 'count': len(investments)}, 'children': [] }
            childrens.append(obj)

            self.before_orgs.append(funding.id)
            c = Counter(self.before_orgs)
            
            if len(investments) > 0 and c[funding.id] < 2:
                for inv in investments:
                    self.before_flow(inv, obj['children'], level+1)

    def after_flow(self, investment, childrens, level=1):

        self.after_investments.append(investment.id)

        # Financiadores
        if investment.recipient_entity_id:
            recipient = investment.funding_entity
            
            investments = InvestmentData.list(funding_entity_id=recipient.entity_id).exclude(pk__in=self.after_investments, created_at__gt=investment.created_at).all()
            #investments = funding.funding_investments.all()

            obj = {'id': 'p_%d_%d' % (level, recipient.entity_id), 'name': recipient.title, 'data': {'level': level, 'css': 'project', 'count': len(investments)}, 'children': [] }

            if level > 1:
                childrens.append(obj)

            self.after_projects.append(recipient.entity_id)
            c = Counter(self.after_projects)

            if len(investments) > 0 and c[recipient.entity_id] < 2:
                for inv in investments:
                    self.after_flow(inv, obj['children'], level+1)

        elif investment.recipient_organization_id:
            recipient = investment.funding_organization

            investments = InvestmentData.list(funding_organization_id=recipient.id).exclude(pk__in=self.after_investments, created_at__gt=investment.created_at).all()
            #investments = funding.funding_investments.all()

            obj = {'id': 'o_%d_%d' % (level, recipient.id), 'name': recipient.name, 'data': {'level': level, 'css': 'organization', 'count': len(investments)}, 'children': [] }

            if level > 1:
                childrens.append(obj)

            self.after_orgs.append(recipient.id)
            c = Counter(self.after_orgs)

            if len(investments) > 0 and c[recipient.id] < 2:
                for inv in investments:
                    self.after_flow(inv, obj['children'], level+1)


    def get(self, request, *args, **kwargs):
        result = {}
        if self.kwargs.has_key('id'):
            id = self.kwargs['id']
            #if not cache.has_key('investment_flow_source_'+str(id)):

            investment = InvestmentData.item(id)
            recipient = None
            funding = None
            obj = None

            if investment is not None:
                if investment.recipient_entity_id: # Projeto Receptor do Investimento
                    recipient = investment.recipient_entity
                    result.update({'id': 'p'+str(recipient.entity_id), 'name': recipient.title, 'data': {'level': 0, 'css': 'project'}, 'children': [] })

                    funding = InvestmentData.list(funding_entity_id = recipient.entity_id)[:1]
                    if not funding and investment.recipient_organization_id:
                        funding = InvestmentData.list(funding_organization_id = investment.recipient_organization_id)[:1]
                        if funding:
                            obj = {'id': 'o'+str(funding.id), 'name': funding.name, 'data': {'level': 0, 'css': 'project'}, 'children': [] }
                    else:
                        obj = {'id': 'p'+str(funding.entity_id), 'name': funding.title, 'data': {'level': 0, 'css': 'project'}, 'children': [] }
                    

                elif investment.recipient_organization_id:
                    recipient = investment.recipient_organization          
                    result.update({'id': 'o'+str(recipient.id), 'name': recipient.name, 'data': {'level': 0, 'css': 'organization'}, 'children': [] })

                    funding = InvestmentData.list(funding_entity_id = recipient.entity_id)[:1]

                if recipient:
                    self.before_flow({
                        'id': investment.id,
                        'funding_entity': investment.funding_entity_id,
                        'funding_organization':investment.funding_organization_id,
                        'created_at':investment.created_at
                    }, result['children'])

                if obj :
                    result['children'].append(obj)
                    self.after_flow(investment, obj['children'])

                    #cache.set('investment_flow_source_'+str(id), result, (60 * 60) * 24)
            #else:
            #    result = cache.get('investment_flow_source_'+str(id))

        return http.HttpResponse(dumps(result, cls=DjangoJSONEncoder), content_type='application/json')

        

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)



class InvestmentMapSourceView(GoogleMapView, BaseDetailView):
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
        if data.has_key('center'):
            c = data.get('center').split(',')
            center = maps.LatLng(c[0], c[1])
        if data.has_key('zoom'):
            zoom = int(data.get('zoom'))
        if data.has_key('mapTypeId'):
            mapTypeId = data.get('mapTypeId')



        if data.has_key('concentration'):
            view = 'concentration'
        gmap = self.get_map(request, center, zoom, mapTypeId)

        sql_columns = """
        a.location_id, 
			a.entity_id,
			sum(c.amount_usd) sum_ammount,
			d.polygon
        """

        if view == 'concentration':
            sql_columns = " min(amount_usd), max(amount_usd) "


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


        if data.has_key('s_organization_type') and data['s_organization_type'] != '':
            sql+=' and exists (select 1 from ecofunds_organization f where f.id in (c.recipient_organization_id, c.funding_organization_id) and f.type_id like %s) '
            query_params.append('%' + data['s_organization_type'] + '%')

        
        if data.has_key('s_country') and data['s_country'] != '':
            sql+=" and cou.name like %s "
            query_params.append('%'+data['s_country'] + '%')

        if data.has_key('s_state') and data['s_state'] != '':
            sql+=" and (d.iso_sub = %s or d.name like %s) "
            query_params.append(data['s_state'])
            query_params.append('%'+data['s_state']+'%')


        
        if data.has_key('s_investment_type') and data['s_investment_type'] != '':
            sql+= " and c.type_id = %s "
            query_params.append(data['s_investment_type'])


        if data.has_key('s_investment_date_from') and data['s_investment_date_from'] != '':
            dt_from = trans_date(data['s_investment_date_from'])
            if dt_from:
                sql+= " and c.created_at >= %s "
                query_params.append(dt_from)


        if data.has_key('s_investment_date_to') and data['s_investment_date_to'] != '':
            dt_to = trans_date(data['s_investment_date_to'])
            if dt_to:
                sql+= " and c.created_at <= %s "
                query_params.append(dt_to)
            

        if view != 'concentration':
            sql+=" group by a.location_id, a.entity_id "

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
                sql+= ' having sum_ammount between %s and %s '
                query_params.append(min_invest)
                query_params.append(max_invest)



        cursor = db.connection.cursor()
        cursor.execute(sql, query_params)
       
        #list = ProjectData.locationFilteredList(request)
            

        if view == 'concentration':
            start, end = 0, 0
            for item in cursor.fetchall():
                if not (item[0] is None):
                    start = float(item[0])
                    end = float(item[1])
            json = {'start': format_currency(start), 'end': format_currency(end)}
            return http.HttpResponse(dumps(json, cls=DjangoJSONEncoder), content_type='application/json')

        points = {}
        

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
                b= False
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
                    text = numbers.format_currency(
                            float(amount),
                            numbers.get_currency_symbol('USD', 'en_US'),
                            u'\xa4\xa4 #,##0.00', locale=request.LANGUAGE_CODE.replace('-', '_')
                        )
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

def remove_investment(request):
    id = request.GET['id']
    try:
        inv = Investment.objects.get(pk=id)
    except Investment.DoesNotExist:
        data = {'status':False}
        return http.HttpResponse(dumps(data,cls=DjangoJSONEncoder),content_type='application/json')
    inv.active=False
    inv.save()
    data = {'status':True}
    return http.HttpResponse(dumps(data,cls=DjangoJSONEncoder),content_type='application/json')


