import logging
import types

from django import db
from django import http
from django.core.cache import cache
from django.http import HttpResponseBadRequest
from django.utils import simplejson as json
from django.views.generic.detail import BaseDetailView
from django.utils.simplejson import dumps, loads
from django.conf import settings

import tablib
from babel import numbers

import pygeoip

from ecofunds.core.models import Organization, ProjectLocation
from ecofunds.maps.forms import OrganizationFilterForm, ProjectFilterForm


log = logging.getLogger('maps')

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

    return lat, lng


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
               u'\xa4\xa4 #,##0.00', locale=settings.LANGUAGE_CODE.replace('-', '_'))


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
        b.website,
        c.id
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
    'organization': 'FROM ecofunds_organization o '
                    'LEFT JOIN ecofunds_locations d ON d.id = o.state_id '
                    'LEFT join ecofunds_countries cou on cou.id = o.country_id '
                    'LEFT JOIN ecofunds_organization_type t ON t.id = o.type_id ',
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
    's_organization_name': {
        'where_data': ' and (o.name like %s or o.acronym like %s) ',
        'parameter': (wrap_like, 's_organization_name', wrap_like, 's_organization_name')
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
    's_organization_type2': {
        'where_data': ' and o.type_id=%s',
        'parameter': ('s_organization_type2')
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

    # workaround bug on 1 string parameter
    # ex: s_project_activity_type
    if isinstance(parameters, str):
        parameters = [parameters]

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

    query_params = []
    possible_filters = filters.keys()

    for filter_id in possible_filters:
        if has_filter(data, filter_id):
            base_query, query_params = apply_filter(filter_id,
                                                    filters,
                                                    data,
                                                    base_query,
                                                    query_params)

    base_query = get_full_query(base_query, domain)
    log.debug(base_query)

    cursor = db.connection.cursor()
    cursor.execute(base_query, query_params)

    return cursor


def project_api(request, map_type):
    if map_type not in ("marker",):
        return HttpResponseBadRequest()

    form = ProjectFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = ProjectLocation.objects.search(**form.cleaned_data)
    qs = qs.only('entity__entity_id', 'location__id', 'entity__title', 'entity__website', 'entity__centroid')

    points = {}

    for obj in qs:
        if obj.entity.centroid:
            lat, lng = parse_centroid(obj.entity.centroid)
        else:
            lat, lng = None, None

        marker = {
            'entity_id': obj.entity.pk,
            'location_id': obj.location.pk,
            'lat': lat,
            'lng': lng,
            'acronym': obj.entity.title,
            'url': obj.entity.website,
        }
        points[obj.entity.pk] = marker

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
        id_ = item[6]

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
                'total_investment_str': format_currency(int_amount),
                'scale': scale,
                'projects': [{
                    'id': id_,
                    'acronym': acronym,
                    'url': url,
                    'entity_id': entity_id,
                    'amount': int_amount,
                    'amount_str': format_currency(int_amount)
                }]
            }
            points[location_id] = marker
        else:
            check_same_entity = False
            for entity in points[location_id]['projects']:
                if entity['entity_id'] == entity_id:
                    check_same_entity = True
            if not check_same_entity:
                proj = {'id': id_,
                        'entity_id': entity_id,
                        'url': url,
                        'amount': int_amount,
                        'amount_str': format_currency(int_amount),
                        'acronym': acronym}
                points[location_id]['projects'].append(proj)
                points[location_id]['total_investment'] += int_amount
                points[location_id]['total_investment_str'] = \
                    localize_currency(points[location_id]['total_investment'], request)

    gmap = {}
    gmap['items'] = points.values()

    return http.HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


def organization_api(request, map_type):
    if map_type not in ("marker", "csv"):
        return HttpResponseBadRequest()

    form = OrganizationFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Organization.objects.search(**form.cleaned_data)
    qs = qs.only('pk', 'name', 'desired_location_lat', 'desired_location_lng')

    if map_type == "csv":
        return output_organization_csv(qs)
    else:
        return output_organization_json(qs)


def output_organization_json(qs):
    points = {}

    for obj in qs:
        marker = {
            'entity_id': obj.pk,
            'name': obj.name.encode('utf-8'),
            'lat': float(str(obj.desired_location_lat)),
            'lng': float(str(obj.desired_location_lng)),
        }

        points[obj.pk] = marker

    gmap = {}
    gmap['items'] = points.values()

    return http.HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


def output_organization_csv(qs):
    data = tablib.Dataset()
    for item in qs:
        data.append([item.id, item.name, item.desired_location_lat, item.desired_location_lng])

    return http.HttpResponse(data.csv, content_type="text/csv")
