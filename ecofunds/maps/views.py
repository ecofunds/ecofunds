from django import db
from django import http
from django.core.cache import cache
from django.utils import simplejson as json
from django.views.generic.detail import BaseDetailView
from django.utils.html import escape
from django.utils.simplejson import dumps, loads

from babel import numbers

from gmapi import maps
from gmapi.maps import Geocoder

import pygeoip

from ecofunds import settings

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

def format_currency(value):
    return numbers.format_currency(
            float(value),
            numbers.get_currency_symbol('USD', 'en_US'),
            u'\xa4\xa4 #,##0.00', locale='pt_BR')

def get_local_lat_lng(request):
    ip = request.META.get('REMOTE_ADDR', None)

    gi = pygeoip.GeoIP(settings.GEOIP_DATABASE, pygeoip.STANDARD)
    record = gi.record_by_addr(ip)

    if record:
        lat = record['latitude']
        lng = record['longitude']
        city = '%s, %s' % (record['city'], record['country_name'])
    else:
        lat = -4.521666
        lng = -58.318725
        city = 'Amazonas, Brasil'

    if not lat or not lng:
        geocoder = Geocoder()
        results, status_code = geocoder.geocode({'address': city })
        if results:
            for r in results:
                lat, lng = r['geometry']['location']['arg']

    return lat, lng

def get_map(request, center_lat_lng=None, zoom=4, mapTypeId=maps.MapTypeId.HYBRID):
    if not center_lat_lng:
        center_lat_lng = get_local_lat_lng(request)

    return {
        'map': {
            'center': center_lat_lng,
            'mapTypeId': mapTypeId,
            'zoom': zoom,
            'minZoom': 2,
            'mapTypeControl': False,
            'zoomControl': False,
            'panControl':False,
            'mapTypeControlOptions': {
                'style': maps.MapTypeControlStyle.HORIZONTAL_BAR
            },
            'streetViewControl': False,
        },
        'items': []
    }

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

def api_error(request, message):
    return http.HttpResponse(dumps(dict(error=message)),
                             content_type="application/json")

def geoapi_map(request, domain, map_type):
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
        center = c[0], c[1]
    if data.has_key('zoom'):
        zoom = int(data.get('zoom'))
    if data.has_key('mapTypeId'):
        mapTypeId = data.get('mapTypeId')

    if domain not in ("project", "investment", "organization"):
        return api_error(request, "Invalid Domain")

    if map_type not in ("concentration", "heat", "density", "bubble"):
        return api_error(request, "Invalid Map Type")

    if domain == "organization" and map_type == "concentration":
        return api_error(request, "Invalid Map Type")

    gmap = get_map(request, center, zoom, mapTypeId)

    select_data = {
        'investment':
        """ SELECT
            a.location_id,
			a.entity_id,
			sum(c.amount_usd) sum_ammount,
			d.centroid
        """,
        'project':
        """ SELECT
            a.location_id,
			a.entity_id,
			count(b.entity_id),
			d.centroid
        """,
        'organization':
        """ SELECT
            o.name,
		    o.desired_location_lat,
		    o.desired_location_lng
        """
    }

    default_from = """
        FROM ecofunds_entity_locations a
        INNER JOIN ecofunds_entities b ON (a.entity_id = b.entity_id)
        INNER JOIN ecofunds_investments c ON  c.recipient_entity_id = b.entity_id
        INNER JOIN ecofunds_locations d ON d.id = a.location_id
        inner join ecofunds_countries cou on cou.id = d.country_id
    """

    from_data = {
        'investment': default_from,
        'project': default_from,
        'organization': 'FROM ecofunds_organization o'
    }

    default_where = 'WHERE b.validated = 1'

    where_data = {
        'investment': default_where,
        'project': default_where,
        'organization': 'WHERE desired_location_lat is not null and '
                        'desired_location_lng is not null'
    }

    if map_type == "concentration":
        sql_columns = "SELECT min(c.amount_usd), max(c.amount_usd) "
    else:
        sql_columns = select_data[domain]

    context = {
        'select_data': sql_columns,
        'from_data': from_data[domain],
        'where_data': where_data[domain]
    }

    base_query = "{select_data} {from_data} {where_data}".format(**context)

    def wrap_like(data_id):
        return "%{0}%".format(data[data_id].encode('utf-8'))

    min_invest = 0
    max_invest = 99999999999

    try:
        min_invest = data['s_investments_from']
        max_invest = data['s_investments_to']
    except Exception as e:
        pass

    filters = {
        's_project_name': {
            'where_data': ' and b.title like %s ',
            'parameter': lambda: (wrap_like('s_project_name'))
        },
        's_project_activity_type': {
            'where_data': ' and exists (select 1 from ecofunds_entity_activities '
                          'e where e.entity_id = b.entity_id and e.activity_id = %s) ',
            'parameter': lambda: (data['s_project_activity_type'])
        },
        's_organization': {
            'where_data': ' and exists (select 1 from ecofunds_organization f '
                          'where f.id in (c.recipient_organization_id, '
                          'c.funding_organization_id) and {fn concat(f.name, '
                          'f.acronym)} like %s) ',
            'parameter': lambda: (wrap_like('s_organization'))
        },
        's_organization_type': {
            'where_data': ' and exists (select 1 from ecofunds_organization f '
                          'where f.id in (c.recipient_organization_id, '
                          'c.funding_organization_id) and f.type_id like %s) ',
            'parameter': lambda: (wrap_like('s_organization_type'))
        },
        's_investment_type': {
            'where_data': ' and c.type_id = %s ',
            'parameter': lambda: (data['s_investment_type'])
        },
        's_country': {
            'where_data': ' and cou.name like %s ',
            'parameter': lambda: (wrap_like('s_country'))
        },
        's_state': {
            'where_data': ' and (d.iso_sub = %s or d.name like %s) ',
            'parameter': lambda: (data['s_state'], wrap_like('s_state'),)
        },
        's_investment_date_from': {
            'where_data': " and c.created_at >= %s "                         \
                          if trans_date('s_investment_date_from') else '',
            'parameter': lambda: (trans_date('s_investment_date_from'))              \
                         if trans_date('s_investment_date_from') else ()
        },
        's_investment_date_to': {
            'where_data': " and c.created_at <= %s "                         \
                          if trans_date('s_investment_date_to') else '',
            'parameter': lambda: (trans_date('s_investment_date_to'))              \
                         if trans_date('s_investment_date_to') else ()
        },
        's_date_from': {
            'where_data': " and b.grant_from >= %s "                         \
                          if trans_date(data.get('s_date_from')) else '',
            'parameter': lambda: (trans_date(data.get('s_date_from')))              \
                         if trans_date(data.get('s_date_from')) else ()
        },
        's_date_to': {
            'where_data': " and b.grant_to <= %s "                         \
                          if trans_date(data.get('s_date_to')) else '',
            'parameter': lambda: (trans_date(data.get('s_date_to')))              \
                         if trans_date(data.get('s_date_to')) else ()
        },
        's_investments_focus': {
            'where_data': 'and exists (select 1 from ecofunds_entity_organizations eo '
                          'inner join ecofunds_entity_activities ea on ea.entity_id = '
                          'eo.entity_id where eo.organization_id = o.id and ea.activity_id = %s)',
            'parameter': lambda: (data['s_investments_focus'])
        }
    }

    def apply_filter(filter_id, context, query, params):
        query = " ".join([query, context[filter_id]['where_data']])
        parameter = context[filter_id]['parameter']()
        if isinstance(parameter, str):
            params.append(parameter)
        else:
            for param in parameter:
                params.append(param)

        return query, params

    def has_filter(filter_id):
        return data.has_key(filter_id) and data[filter_id] != ''

    query_params = []
    possible_filters = filters.keys()

    for filter_id in possible_filters:
        if has_filter(filter_id):
            base_query, query_params = apply_filter(filter_id,
                                                    filters,
                                                    base_query,
                                                    query_params)

    group_by = {
        'project': ' group by a.location_id ',
        'investment': ' group by a.location_id, a.entity_id ',
        'organization': 'group by o.name, o.desired_location_lat, o.desired_location_lat '
    }

    base_query = "{base_query} {group_by}".format(base_query=base_query,
                                                  group_by=group_by[domain])

    having = {
        's_investments_from': {
            'where_data': ' having sum_ammount between %s and %s ',
            'parameter': lambda: (float(min_invest),
                                  float(max_invest))
        },
        's_estimated_investments_value_from': {
            'where_data': ' having sum(i.amount_usd) between %s and %s ',
            'parameter': lambda: (float(min_invest),
                                  float(max_invest))
        }
    }

    possible_filters = having.keys()

    for filter_id in possible_filters:
        if has_filter(filter_id):
            base_query, query_params = apply_filter(filter_id,
                                                    having,
                                                    base_query,
                                                    query_params)

    cursor = db.connection.cursor()
    cursor.execute(base_query, query_params)

    if map_type == "concentration":
        start, end = 0, 0
        cursor = db.connection.cursor()
        cursor.execute(base_query, query_params)
        for item in cursor.fetchall():
            if not (item[0] is None):
                start = float(item[0])
                end = float(item[1])
        json = {'start': format_currency(start), 'end': format_currency(end),
                'query': base_query}
        return http.HttpResponse(dumps(json), content_type='application/json')

    for item in cursor.fetchall():
        location_id = item[0]
        entity_id = item[1]
        amount = item[2]
        centroid = item[3]

        marker = {
            'location_id': location_id,
            'entity_id': entity_id,
            'amount': str(item[2]),
            'centroid': centroid
        }

        gmap['items'].append(marker)

    return http.HttpResponse(dumps(dict(map=gmap,
                                            query=base_query,
                                            params=query_params)),
                             content_type="application/json")
