from django.utils.datetime_safe import datetime
from decimal import Decimal
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.utils.simplejson import dumps
import tablib
from babel import numbers
from ecofunds.crud.models import Organization2

from ecofunds.core.models import Organization, ProjectLocation, Project, Investment
from ecofunds.crud.models import Project2, Organization2, Investment2
from ecofunds.maps.forms import OrganizationFilterForm, ProjectFilterForm, InvestmentFilterForm
from ecofunds.maps.utils import parse_centroid


class DownloadResponse(HttpResponse):
    def __init__(self, content='', mimetype=None, status=None, content_type=None, filename=None):
        super(DownloadResponse, self).__init__(content, mimetype, status, content_type)

        if filename:
            self['Content-Disposition'] = 'attachment; filename="%s"' % filename


def format_currency(value):
    return numbers.format_currency(
            float(value),
            numbers.get_currency_symbol('USD', 'en_US'),
            u'\xa4\xa4 #,##0.00', locale='pt_BR')


PROJECT_HEADERS = ['NAME', 'ACRONYM', 'ACTIVITY_TYPE', 'DESCRIPTION',
                   'URL', 'EMAIL', 'PHONE', 'LAT', 'LNG']

PROJECT_EXPORT_COLUMNS = {
    'NAME': 'name',
    'ACRONYM': 'acronym',
    'ACTIVITY_TYPE': 'activities_names',
    'DESCRIPTION': 'description',
    'URL': 'url',
    'EMAIL': 'email',
    'PHONE': 'phone',
    'LAT': 'location__latitude',
    'LNG': 'location__longitude'
}

#TODO missing attributes
#'ACTIVITIES': 'activities',
#"start_date",
#"end_date",
#"address",
#"zipcode"


def project_api(request, map_type):
    if map_type not in ("marker", "csv", "xls"):
        return HttpResponseBadRequest()

    form = ProjectFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Project2.objects.search(**form.cleaned_data)

    if map_type == "csv":
        return output_project_csv(qs)
    elif map_type == "xls":
        return output_project_excel(qs)
    else:
        return output_project_json(qs)


def project_marker(obj):
    return {
        'id': obj.pk,
        'lat': obj.latitude,
        'lng': obj.longitude,
        'name': obj.name,
        'acronym': obj.acronym,
        'url': obj.url,
        'link': obj.get_absolute_url(),
    }

def output_project_json(qs):
    points = {}
    for obj in qs:
        points[obj.pk] = project_marker(obj)

    gmap = {}
    gmap['items'] = points.values()

    return HttpResponse(dumps(dict(map=gmap)), content_type="application/json")

def lookup_attr(obj, lookup):
    (attr, sep, tail_lookup) = lookup.partition('__')

    try:
        value = getattr(obj, attr)
        if hasattr(value, '__call__'):
            return value()
        if tail_lookup:
            return lookup_attr(value, tail_lookup)
        else:
            return value
    except Exception as e:
        return ''

def output_project_csv(qs):
    data = tablib.Dataset(PROJECT_HEADERS)
    for item in qs:
        row = []
        for key in PROJECT_HEADERS:
            row.append(lookup_attr(item, PROJECT_EXPORT_COLUMNS[key]) or 'None')
        data.append(row)

    response = HttpResponse(data.csv, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="projects.csv"'
    return response


def output_project_excel(qs):
    import xlwt
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="projects.xls"'

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Projects')

    for i, header in enumerate(PROJECT_HEADERS):
        ws.write(0, i, header)

    for i, item in enumerate(qs):
        row = []
        for j, key in enumerate(PROJECT_HEADERS):
            data = lookup_attr(item, PROJECT_EXPORT_COLUMNS[key])
            if data and isinstance(data, unicode) and len(data) > 3000:
                data = data[:3000]
            ws.write(i+1, j, data)

    wb.save(response)

    return response


INVESTMENT_HEADERS = [
    'KIND',
    'AMOUNT',
    'RECP ORG',
    'RECP PROJECT',
    'RECP PROJECT ACRONYM',
    'RECP PROJECT DESC',
    'RECP PROJECT ACTIVITIES',
    'RECP PROJECT GEOFOCUS',
    'FUND ORG',
    'FUND PROJ',
    'FUND PROJ ACRONYM',
    'CONTRIBUTED AT',
    'COMPLETED AT',
]

INVESTMENT_COLUMNS = {
    'KIND': 'get_kind_display',
    'AMOUNT': 'amount',
    'RECP ORG': 'recipient_organization__name',
    'RECP PROJECT': 'recipient_project__name',
    'RECP PROJECT ACRONYM': 'recipient_project__acronym',
    'RECP PROJECT DESC': 'recipient_project__description',
    'RECP PROJECT ACTIVITIES': 'recipient_project__activities_names',
    'RECP PROJECT GEOFOCUS': 'recipient_project__geofocus',
    'FUND ORG': 'funding_organization__name',
    'FUND PROJ': 'funding_project__name',
    'FUND PROJ ACRONYM': 'funding_project__acronym',
    'CONTRIBUTED AT': 'contributed_at',
    'COMPLETED AT': 'completed_at',
}

def investment_to_csv(items):
    table = tablib.Dataset(INVESTMENT_HEADERS)

    for item in items:
        row = []
        for header in INVESTMENT_HEADERS:
            row.append(lookup_attr(item, INVESTMENT_COLUMNS[header]))
        table.append(row)

    return table.csv


def investment_to_xls(items):
    import xlwt
    from StringIO import StringIO
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Investments')

    currency_style = xlwt.XFStyle()
    currency_style.num_format_str = "#,##0.00"

    date_style = xlwt.XFStyle()
    date_style.num_format_str = "YYYY-MM-DD"

    for col, header in enumerate(INVESTMENT_HEADERS):
        ws.write(0, col, header)

    for idx, item in enumerate(items):
        r = idx + 1 # 1st row is #1

        for c, header in enumerate(INVESTMENT_HEADERS):
            value = lookup_attr(item, INVESTMENT_COLUMNS[header])

            if isinstance(value, (float, Decimal)):
                ws.write(r, c, int(value), style=currency_style)
            elif isinstance(value, datetime):
                ws.write(r, c, value, style=date_style)
            else:
                ws.write(r, c, value)

    content = StringIO()
    wb.save(content)
    return content


def investment_to_marker(items):
    points = {}

    for item in items:
        loc = item.recipient_project.location
        # Insert new location into points
        if not loc.pk in points:
            points[loc.pk] = {
                'location_id': loc.pk,
                'lat': loc.latitude,
                'lng': loc.longitude,
                'total_investment': float(0),
                'total_investment_str': format_currency(0),
                'investments': []
            }

        investment = {
            'id': item.pk,
            'amount': float(item.amount),
            'amount_str': format_currency(item.amount),
            'recipient_name': item.recipient_project.name,
            'link': item.get_absolute_url(),
        }

        points[loc.pk]['investments'].append(investment)
        points[loc.pk]['total_investment'] += float(item.amount)
        points[loc.pk]['total_investment_str'] = format_currency(points[loc.pk]['total_investment'])

    return points.values()


def investment_api(request, map_type):
    if map_type not in ("density", "csv", "xls"):
        return HttpResponseBadRequest()

    form = InvestmentFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Investment2.objects.search(**form.cleaned_data)
    qs = qs.select_related('funding_organization', 'funding_project', 'recipient_organization', 'recipient_project', 'recipient_project__location')

    if map_type == "csv":
        return DownloadResponse(investment_to_csv(qs), content_type="text/csv", filename='investments.csv')
    elif map_type == "xls":
        return DownloadResponse(investment_to_xls(qs), content_type="application/ms-excel", filename='investments.xls')
    else:
        content = dict(map=dict(items=investment_to_marker(qs)))
        return HttpResponse(dumps(content), content_type="application/json")


ORGANIZATION_EXPORT_COLUMNS = {
    'NAME': 'name',
    'DESCRIPTION': 'description',
    'ORG. TYPE': 'kind',
    'ADDRESS': 'address',
    'ZIPCODE': 'zipcode',
    'COUNTRY': 'country',
    'STATE': 'state',
    'CITY': 'city',
    'EMAIL': 'email',
    'URL':  'url',
    'PHONE': 'phone',
    'LAT': 'location__latitude',
    'LNG': 'location__longitude',
}


ORGANIZATION_HEADERS = ['NAME', 'DESCRIPTION', 'ORG. TYPE', 'ADDRESS', 'ZIPCODE', 'COUNTRY', 'STATE', 'CITY',
                        'EMAIL', 'URL' , 'PHONE', 'LAT', 'LNG']


def organization_api(request, map_type):
    if map_type not in ("marker", "csv", "xls"):
        return HttpResponseBadRequest()

    form = OrganizationFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Organization2.objects.search(**form.cleaned_data)

    if map_type == "csv":
        return output_organization_csv(qs)
    elif map_type == "xls":
        return output_organization_excel(qs)
    else:
        return output_organization_json(qs)


def output_organization_json(qs):
    points = {}

    for obj in qs:
        marker = {
            'id': obj.pk,
            'name': obj.name,
            'acronym': obj.acronym,
            'lat': obj.latitude,
            'lng': obj.longitude,
            'link': obj.get_absolute_url(),
        }

        points[obj.pk] = marker

    gmap = {}
    gmap['items'] = points.values()

    return HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


def output_organization_csv(qs):
    data = tablib.Dataset(ORGANIZATION_HEADERS)
    for item in qs:
        row = []
        for key in ORGANIZATION_HEADERS:
            row.append(lookup_attr(item, ORGANIZATION_EXPORT_COLUMNS[key]) or 'None')
        data.append(row)

    response = HttpResponse(data.csv, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="organizations.csv"'
    return response

def output_organization_excel(qs):
    import xlwt
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="organizations.xls"'

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Organizations')

    for i, header in enumerate(ORGANIZATION_HEADERS):
        ws.write(0, i, header)

    for i, item in enumerate(qs):
        row = []
        for j, key in enumerate(ORGANIZATION_HEADERS):
            ws.write(i+1, j, lookup_attr(item, ORGANIZATION_EXPORT_COLUMNS[key]))

    wb.save(response)

    return response


def map_view(request):
    context = {
        'search_project_form': ProjectFilterForm(request.GET),
        'search_organization_form': OrganizationFilterForm(request.GET),
        'search_investment_form': InvestmentFilterForm(request.GET),
    }
    context.update(Project.objects.stats())
    context.update(Organization.objects.stats())
    context.update(Investment.objects.stats())

    return render(request, "maps/map.html", context)
