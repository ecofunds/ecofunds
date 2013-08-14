import logging
import math
import sys
import time

from collections import Counter

from django import db
from django import http
from django.core.cache import cache
from django.db.models import Count
from django.utils.simplejson import dumps, loads
from django.views.generic.detail import BaseDetailView
from django.conf import settings

from ecofunds.business import ProjectData, OrganizationData, InvestmentData
from ecofunds.core.views import DjangoJSONEncoder
from ecofunds.maps.models import GoogleMapView
from ecofunds.core.models import Investment
from ecofunds.colors_RdYlGn import scale as color_scale

from gmapi.maps import MapConstantClass, MapClass, Args
from BeautifulSoup import BeautifulSoup
from gmapi import maps
from babel import numbers

log = logging.getLogger(__name__)

sys.setrecursionlimit(10000)
SymbolPath = MapConstantClass('SymbolPath', ('CIRCLE',))

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
