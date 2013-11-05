# coding: utf-8
import xlwt
from datetime import date
from decimal import Decimal
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.utils.simplejson import dumps
import tablib
from babel import numbers
from ecofunds.crud.models import Project2, Organization2, Investment2
from ecofunds.maps.forms import OrganizationFilterForm, ProjectFilterForm, InvestmentFilterForm


class DownloadResponse(HttpResponse):
    def __init__(self, content='', mimetype=None, status=None, content_type=None, filename=None):
        super(DownloadResponse, self).__init__(content, mimetype, status, content_type)

        if filename:
            self['Content-Disposition'] = 'attachment; filename="%s"' % filename


def format_currency(value):
    return numbers.format_currency(
            value,
            numbers.get_currency_symbol('USD', 'en_US'),
            u'\xa4\xa4 #,##0.00', locale='en_US')


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


def queryset_to_csv(items, headers, column_map):
    table = tablib.Dataset(headers)
    for item in items:
        row = []
        for header in headers:
            row.append(lookup_attr(item, column_map[header]))
        table.append(row)

    return table.csv


def queryset_to_xls(items, output, sheet_name, headers, column_map):
    wb = xlwt.Workbook()
    ws = wb.add_sheet(sheet_name)

    XLS_MAX_LEN = 3000

    currency_style = xlwt.XFStyle()
    currency_style.num_format_str = "#,##0.00"

    date_style = xlwt.XFStyle()
    date_style.num_format_str = "YYYY-MM-DD"

    for col, header in enumerate(headers):
        ws.write(0, col, header)

    for idx, item in enumerate(items):
        r = idx + 1 # 1st row is #1

        for c, header in enumerate(headers):
            value = lookup_attr(item, column_map[header])

            #if header.endswith('AT'):
            #    import ipdb; ipdb.set_trace()

            if isinstance(value, unicode) and len(value) > XLS_MAX_LEN:
                ws.write(r, c, value[:XLS_MAX_LEN])
            elif isinstance(value, Decimal):
                ws.write(r, c, int(value), style=currency_style)
            elif isinstance(value, date):
                ws.write(r, c, value, style=date_style)
            else:
                ws.write(r, c, value)

    wb.save(output)


PROJECT_HEADERS = ['NAME', 'ACRONYM', 'ACTIVITY_TYPE', 'DESCRIPTION',
                   'URL', 'EMAIL', 'PHONE', 'LAT', 'LNG']

PROJECT_COLUMNS = {
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


def projects_to_marker(items):
    points = {}
    for item in items:
        points[item.pk] = dict(
            id=item.pk,
            lat=item.latitude,
            lng=item.longitude,
            name=item.name,
            acronym=item.acronym,
            url=item.url,
            link=item.get_absolute_url(),
        )

    return points.values()


def project_api(request, map_type):
    map_type = map_type or "marker" #default

    if map_type not in ("marker", "csv", "xls"):
        return HttpResponseBadRequest()

    form = ProjectFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Project2.objects.search(**form.cleaned_data)

    if map_type == "csv":
        content = queryset_to_csv(qs, PROJECT_HEADERS, PROJECT_COLUMNS)
        return DownloadResponse(content, content_type="text/csv", filename='projects.csv')
    elif map_type == "xls":
        response = DownloadResponse(content_type="application/ms-excel", filename='projects.xls')
        queryset_to_xls(qs, response, 'Projects', PROJECT_HEADERS, PROJECT_COLUMNS)
        return response
    else:
        content = dict(map=dict(items=projects_to_marker(qs)))
        return HttpResponse(dumps(content), content_type="application/json")



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


def investments_to_marker(items):
    points = {}

    for item in items:
        loc = item.recipient_project.location
        # Insert new location into points
        if not loc.pk in points:
            points[loc.pk] = {
                'location_id': loc.pk,
                'lat': loc.latitude,
                'lng': loc.longitude,
                'total_investment': 0,
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
        points[loc.pk]['total_investment'] += item.amount
        points[loc.pk]['total_investment_str'] = format_currency(points[loc.pk]['total_investment'])

    for k, v in points.items():
        v['total_investment_str'] = format_currency(v['total_investment'])
        v['total_investment'] = int(v['total_investment'])

    return points.values()


def investment_api(request, map_type):
    map_type = map_type or "density" #default

    if map_type not in ("density", "csv", "xls"):
        return HttpResponseBadRequest()

    form = InvestmentFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Investment2.objects.search(**form.cleaned_data)
    qs = qs.select_related('funding_organization', 'funding_project', 'recipient_organization', 'recipient_project', 'recipient_project__location')

    if map_type == "csv":
        content = queryset_to_csv(qs, INVESTMENT_HEADERS, INVESTMENT_COLUMNS)
        return DownloadResponse(content, content_type="text/csv", filename='investments.csv')
    elif map_type == "xls":
        response = DownloadResponse(content_type="application/ms-excel", filename='investments.xls')
        queryset_to_xls(qs, response, 'Investments', INVESTMENT_HEADERS, INVESTMENT_COLUMNS)
        return response
    else:
        content = dict(map=dict(items=investments_to_marker(qs)))
        return HttpResponse(dumps(content), content_type="application/json")


ORGANIZATION_HEADERS = [
    'NAME',
    'DESCRIPTION',
    'ORG. TYPE',
    'ADDRESS',
    'ZIPCODE',
    'COUNTRY',
    'STATE',
    'CITY',
    'EMAIL',
    'URL',
    'PHONE',
    'LAT',
    'LNG',
]


ORGANIZATION_COLUMNS = {
    'NAME': 'name',
    'DESCRIPTION': 'description',
    'ORG. TYPE': 'get_kind_display',
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


def organizations_to_marker(items):
    points = {}

    for item in items:
        points[item.pk] = {
            'id': item.pk,
            'name': item.name,
            'acronym': item.acronym,
            'lat': item.latitude,
            'lng': item.longitude,
            'link': item.get_absolute_url(),
        }

    return points.values()


def organization_api(request, map_type):
    map_type = map_type or "marker" #default

    if map_type not in ("marker", "csv", "xls"):
        return HttpResponseBadRequest()

    form = OrganizationFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Organization2.objects.search(**form.cleaned_data)

    if map_type == "csv":
        content = queryset_to_csv(qs, ORGANIZATION_HEADERS, ORGANIZATION_COLUMNS)
        return DownloadResponse(content, content_type="text/csv", filename='organizations.csv')
    elif map_type == "xls":
        response = DownloadResponse(content_type="application/ms-excel", filename='organizations.xls')
        queryset_to_xls(qs, response, 'Organizations', ORGANIZATION_HEADERS, ORGANIZATION_COLUMNS)
        return response
    else:
        content = dict(map=dict(items=organizations_to_marker(qs)))
        return HttpResponse(dumps(content), content_type="application/json")


def map_view(request):
    context = {
        'search_project_form': ProjectFilterForm(request.GET),
        'search_organization_form': OrganizationFilterForm(request.GET),
        'search_investment_form': InvestmentFilterForm(request.GET),
    }
    context.update(Project2.objects.stats())
    context.update(Organization2.objects.stats())
    context.update(Investment2.objects.stats())

    return render(request, "maps/map.html", context)
