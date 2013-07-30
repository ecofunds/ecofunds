import logging
import types

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


log = logging.getLogger(__name__)

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

def localize_currency(number, request):
    return numbers.format_currency(number,
               numbers.get_currency_symbol('USD', 'en_US'),
               u'\xa4\xa4 #,##0.00', locale=request.LANGUAGE_CODE.replace('-', '_'))


def api_error(request, message):
    return http.HttpResponse(dumps(dict(error=message)),
                             content_type="application/json")

def wrap_like(data):
    return "%{0}%".format(data.encode('utf-8'))

select_data = {
    'investment':
    """ SELECT
        a.location_id,
        a.entity_id,
        sum(c.amount_usd) sum_ammount,
        d.centroid,
        b.title,
        b.website
    """,
    'project':
    """ SELECT
        a.entity_id,
        a.location_id,
        b.centroid,
        b.title,
        b.website
    """,
    'organization':
    """ SELECT
        o.id,
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
    'organization': 'FROM ecofunds_organization o ',
}

default_where = 'WHERE b.validated = 1'

where_data = {
    'investment': default_where,
    'project': default_where,
    'organization': 'WHERE desired_location_lat is not null and '
                    'desired_location_lng is not null'
}


filters = {
    's_project_name': {
        'where_data': ' and b.title like %s ',
        'parameter': (wrap_like, 's_project_name')
    },
    's_project_activity_type': {
        'where_data': ' and exists (select 1 from ecofunds_entity_activities '
                        'e where e.entity_id = b.entity_id and e.activity_id = %s) ',
        'parameter': ('s_project_activity_type')
    },
    's_organization': {
        'where_data': ' and exists (select 1 from ecofunds_organization f '
                        'where f.id in (c.recipient_organization_id, '
                        'c.funding_organization_id) and {fn concat(f.name, '
                        'f.acronym)} like %s) ',
        'parameter': (wrap_like, 's_organization')
    },
    's_organization_type': {
        'where_data': ' and exists (select 1 from ecofunds_organization f '
                        'where f.id in (c.recipient_organization_id, '
                        'c.funding_organization_id) and f.type_id like %s) ',
        'parameter': (wrap_like, 's_organization_type')
    },
    's_investment_type': {
        'where_data': ' and c.type_id = %s ',
        'parameter': ('s_investment_type')
    },
    's_country': {
        'where_data': ' and cou.name like %s ',
        'parameter': (wrap_like, 's_country')
    },
    's_state': {
        'where_data': ' and (d.iso_sub = %s or d.name like %s) ',
        'parameter': ('s_state', wrap_like, 's_state')
    },
    's_investment_date_from': {
        'where_data': " and c.created_at >= %s ",
        'parameter': (trans_date, 's_investment_date_from')
    },
    's_investment_date_to': {
        'where_data': " and c.created_at <= %s ",
        'parameter': (trans_date, 's_investment_date_to')
    },
    's_date_from': {
        'where_data': " and b.grant_from >= %s ",
        'parameter': (trans_date, 's_date_from')
    },
    's_date_to': {
        'where_data': " and b.grant_to <= %s ",
        'parameter':  (trans_date, 's_date_to')
    },
    's_investments_focus': {
        'where_data': 'and exists (select 1 from ecofunds_entity_organizations eo '
                        'inner join ecofunds_entity_activities ea on ea.entity_id = '
                        'eo.entity_id where eo.organization_id = o.id and ea.activity_id = %s)',
        'parameter': ('s_investments_focus')
    }
}

group_by = {
    'project': '',
    'investment': ' group by a.location_id, a.entity_id ',
    'organization': 'group by o.name, o.desired_location_lat, o.desired_location_lat '
}



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


def get_base_query(domain):
    sql_columns = select_data[domain]

    context = {
        'select_data': sql_columns,
        'from_data': from_data[domain],
        'where_data': where_data[domain]
    }

    base_query = "{select_data} {from_data} {where_data}".format(**context)
    return base_query

def get_full_query(base_query, domain):
    base_query = "{base_query} {group_by}".format(base_query=base_query,
                                                  group_by=group_by[domain])
    return base_query

def resolve(parameters, context):
    _return = []
    _stacked_function = None
    for parameter in parameters:
        if isinstance(parameter, str):
            if _stacked_function:
                _return.append(_stacked_function(context[parameter]))
            else:
                _return.append(context[parameter])
            _stacked_function = None
        elif isinstance(parameter, types.FunctionType):
            _stacked_function = parameter
    return _return


def apply_filter(filter_id, filters, context, query, params):
    query = " ".join([query, filters[filter_id]['where_data']])
    parameters = filters[filter_id]['parameter']
    params.extend(resolve(parameters, context))
    return query, params


def has_filter(data, filter_id):
    return data.has_key(filter_id) and data[filter_id] != ''


def parse_centroid(centroid):
    latlng = centroid.split(',')
    x = float(latlng[0].strip())
    y = float(latlng[1].strip())
    return (x, y)


def _get_api_cursor(request, domain):
    if request.method == "POST":
        data = request.POST
    else:
        data = request.GET

    base_query = get_base_query(domain)
    base_query = get_full_query(base_query, domain)

    query_params = []
    possible_filters = filters.keys()

    for filter_id in possible_filters:
        if has_filter(data, filter_id):
            base_query, query_params = apply_filter(filter_id,
                                                    filters,
                                                    data,
                                                    base_query,
                                                    query_params)

    possible_filters = having.keys()

    for filter_id in possible_filters:
        if has_filter(data, filter_id):
            base_query, query_params = apply_filter(filter_id,
                                                    having,
                                                    base_query,
                                                    query_params)

    cursor = db.connection.cursor()
    cursor.execute(base_query, query_params)

    log.debug(base_query)

    return cursor


def project_api(request, map_type):
    if map_type not in ("concentration", "heat", "density", "marker"):
        return api_error(request, "Invalid Map Type")

    cursor = _get_api_cursor(request, 'project')

    points = {}

    for item in cursor.fetchall():
        log.debug(item)

        entity_id = item[0]
        location_id = item[1]
        centroid = item[2]
        acronym = item[3]
        url = item[4]

        lat = None
        lng = None

        if centroid:
            lat = parse_centroid(centroid)[0]
            lng = parse_centroid(centroid)[1]

        marker = {
            'entity_id': entity_id,
            'location_id': location_id,
            'lat': lat,
            'lng': lng,
            'acronym': acronym,
            'url': url,
        }
        points[entity_id] = marker


    gmap = {}
    gmap['items'] = points.values()

    return http.HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


def investment_api(request, map_type):
    if map_type not in ("density"):
        return api_error(request, "Invalid Map Type")

    cursor = _get_api_cursor(request, 'investment')

    points = {}

    for item in cursor.fetchall():
        location_id = item[0]
        entity_id = item[1]
        int_amount = int(item[2])
        str_amount = str(item[2])
        centroid = item[3]
        acronym = item[4]
        url = item[5]

        lat = None
        lng = None

        if centroid:
            lat = parse_centroid(centroid)[0]
            lng = parse_centroid(centroid)[1]

        if not location_id in points:
            scale = 30
            if map_type == "density":
                scale = (len(str_amount)+1) * 3

            str_amount = localize_currency(int_amount, request)

            marker = {
                'location_id': location_id,
                'lat': lat,
                'lng': lng,
                'total_investment': int_amount,
                'total_investment_str': str_amount,
                'scale': scale,
                'projects': [{
                    'acronym': acronym,
                    'url': url,
                    'entity_id': entity_id,
                    'amount': int_amount
                }]
            }
            points[location_id] = marker
        else:
            check_same_entity = False
            for entity in points[location_id]['projects']:
                if entity['entity_id'] == entity_id:
                    check_same_entity = True
            if not check_same_entity:
                proj = {'entity_id': entity_id,
                        'url': url,
                        'amount': int_amount,
                        'acronym': acronym}
                points[location_id]['projects'].append(proj)
                points[location_id]['total_investment'] += int_amount
                points[location_id]['total_investment_str'] = \
                    localize_currency(points[location_id]['total_investment'], request)

    gmap = {}
    gmap['items'] = points.values()

    return http.HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


def organization_api(request, map_type):
    if map_type not in ("marker"):
        return api_error(request, "Invalid Map Type")

    cursor = _get_api_cursor(request, 'organization')

    points = {}

    for item in cursor.fetchall():
        organization_id = item[0]
        name = item[1].encode('utf-8')
        lat = float(item[2])
        lng = float(item[3])

        marker = {
            'entity_id': organization_id,
            'name': name,
            'lat': lat,
            'lng': lng,
        }

        points[organization_id] = marker

    gmap = {}
    gmap['items'] = points.values()

    return http.HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


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

    if map_type not in ("concentration", "heat", "density", "marker"):
        return api_error(request, "Invalid Map Type")

    if domain == "organization" and map_type == "concentration":
        return api_error(request, "Invalid Map Type")

    gmap = get_map(request, center, zoom, mapTypeId)

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

    #TODO concentration maybe should be another view
    if map_type != "concentration":
        group_by = {
            'project': '',
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

    points = {}

    for item in cursor.fetchall():
        log.debug(item)

        if domain == 'project':
            entity_id = item[0] if len(item) > 0 else None
            location_id = item[1] if len(item) > 1 else None
            centroid = item[2]
            acronym = item[3]
            url = item[4]
            str_amount = '0'
            int_amount = 0
        else:
            location_id = item[0] if len(item) > 0 else None
            entity_id = item[1] if len(item) > 1 else None
            int_amount = int(item[2]) if len(item) > 2 else None
            str_amount = str(item[2]) if len(item) > 2 else None
            centroid = item[3] if len(item) > 3 else None
            acronym = item[4] if len(item) > 4 else None
            url = item[5] if len(item) > 6 else None

        def parse_centroid(centroid):
            latlng = centroid.split(',')
            x = float(latlng[0].strip())
            y = float(latlng[1].strip())
            return (x, y)

        lat = None
        lng = None

        if centroid:
            lat = parse_centroid(centroid)[0]
            lng = parse_centroid(centroid)[1]

        if domain == "organization":
            name = location_id.encode('utf-8')
            entity_id = None
            int_amount = None
            str_amount = None
            lat = float(item[1])
            lng = float(item[2])

        if not location_id in points:

            scale = 30
            if domain in ('investment', 'project') and map_type == "density":
                scale = (len(str_amount)+1) * 3
                if domain == "investment":
                    str_amount = localize_currency(int_amount, request)

            marker = {
                'location_id': location_id,
                'lat': lat,
                'lng': lng,
                'total_investment': int_amount,
                'total_investment_str': str_amount,
                'scale': scale,
                'projects': [{
                    'acronym': acronym,
                    'url': url,
                    'entity_id': entity_id,
                    'amount': int_amount
                }]
            }
            points[location_id] = marker
        else:
            check_same_entity = False
            for entity in points[location_id]['projects']:
                if entity['entity_id'] == entity_id:
                    check_same_entity = True
            if not check_same_entity:
                proj = {'entity_id': entity_id,
                        'url': url,
                        'amount': int_amount,
                        'acronym': acronym}
                points[location_id]['projects'].append(proj)
                points[location_id]['total_investment'] += int_amount
                points[location_id]['total_investment_str'] = \
                    localize_currency(points[location_id]['total_investment'], request)

    gmap['items'] = points.values()

    if len(points) > 0 and domain != 'organization':
        sum_inv = sum(points[key]['total_investment'] for key in points)
        max_inv = max(points[key]['total_investment'] for key in points)
        min_inv = min(points[key]['total_investment'] for key in points)


    return http.HttpResponse(dumps(dict(map=gmap,
                                            query=base_query,
                                            params=query_params)),
                             content_type="application/json")
