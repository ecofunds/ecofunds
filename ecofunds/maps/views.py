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


INVESTMENT_EXPORT_COLUMNS = {
    'KIND': 'get_kind_display',
    'AMOUNT': 'amount',
    'RECP ORG NAME': 'recipient_organization__name',
    'RECP PROJECT ACRONYM': 'recipient_project__acronym',
    'RECP PROJECT NAME': 'recipient_project__name',
    'RECP PROJECT DESC': 'recipient_project__desc',
    'RECP PROJECT ACTIVITIES': 'recipient_project__activities_names',
    'RECP PROJECT GEOFOCUS': 'recipient_project__geofocus',
    'FUNDING ORG NAME': 'funding_organization__name',
    'FUNDING PROJ NAME': 'funding_project__name',
    'FUNDING PROJ ACRONYM': 'funding_project__acronym',
    'CONTRIBUTED AT': 'contributed_at',
    'COMPLETED AT': 'completed_at'
   # 'LOCATION': 'recipient_project__location__name',
   # 'COUNTRY': 'recipient_project__country',
   # 'LAT': 'recipient_project__location__latitude',
   # 'LNG': 'recipient_project__location__longitude',
}

'''
    kind
    amount
#recipient_project.kind
    recipient_organization.name
    recipient_project.acronym
    recipient_project.name
    recipient_project.description
    recipient_project.activities
    recipient_project.geofocus
    funding_organization.name
    funding_project.name
    funding_project.acronym
    contributed_at
    completed_at
'''

INVESTMENT_HEADERS = ['KIND', 'AMOUNT', 'RECP ORG NAME' ,'RECP PROJECT NAME',
                      'RECP PROJECT ACRONYM', 'RECP PROJECT DESC',
                      'RECP PROJECT ACTIVITIES', 'RECP PROJECT GEOFOCUS',
                      'FUNDING ORG NAME', 'FUNDING PROJ NAME',
                      'FUNDING PROJ ACRONYM', 'CONTRIBUTED AT',
                      'COMPLETED AT']

def investment_api(request, map_type):
    if map_type not in ("density", "csv", "xls"):
        return HttpResponseBadRequest()

    form = InvestmentFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Investment2.objects.search(**form.cleaned_data)
    qs = qs.select_related('funding_organization', 'funding_project', 'recipient_organization', 'recipient_project', 'recipient_project__location')

    points = {}

    items = None
    if map_type == "density":
        for obj in qs:
            project = {
                'id': obj.pk, # Should be investment ID, but it's not possible
                'amount': float(obj.amount),
                'amount_str': format_currency(obj.amount)
            }

            if not obj.recipient_project:
                continue

            if obj.recipient_project:
                project['recipient_project_id'] = obj.recipient_project.pk
                project['recipient_project'] = project_marker(obj.recipient_project)

            if obj.funding_project:
                project['funding_project_id'] = obj.funding_project.pk
                project['funding_project'] = project_marker(obj.funding_project)

            if not obj.recipient_project.location.pk in points:
                points[obj.recipient_project.location.pk] = {
                    'location': obj.recipient_project.location.name,
                    'location_id': obj.recipient_project.location.pk,
                    'lat': obj.recipient_project.latitude,
                    'lng': obj.recipient_project.longitude,
                    'total_investment': float(obj.amount),
                    'total_investment_str': format_currency(obj.amount),
                    'projects': [project]
                }
            else:
                points[obj.recipient_project.location.pk]['projects'].append(project)
                points[obj.recipient_project.location.pk]['total_investment'] += float(obj.amount)
                points[obj.recipient_project.location.pk]['total_investment_str'] = format_currency(points[obj.recipient_project.location.pk]['total_investment'])

        items =  points.values()
    else:
        items = []
        for obj in qs:
            items.append(obj)

    if map_type == "csv":
        return output_investment_csv(items)
    elif map_type == "xls":
        return output_investment_excel(items)
    else:
        return output_investment_json(items)


def output_investment_json(items):
    gmap = {}
    gmap['items'] = items

    return HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


def output_investment_csv(items):
    data = tablib.Dataset(INVESTMENT_HEADERS)
    for item in items:
        row = []
        for key in INVESTMENT_HEADERS:
            col_data = lookup_attr(item, INVESTMENT_EXPORT_COLUMNS[key])
            row.append(col_data)
        data.append(row)

    response = HttpResponse(data.csv, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="investment.csv"'
    return response


def output_investment_excel(items):
    import xlwt
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="investment.xls"'

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Investments')

    currency_style = xlwt.XFStyle()
    currency_style.num_format_str = "#,##0.00"

    date_style = xlwt.XFStyle()
    date_style.num_format_str = "YYYY-MM-DD"

    for i, header in enumerate(INVESTMENT_HEADERS):
        ws.write(0, i, header)

    for i, item in enumerate(items):
        row = []
        for j, key in enumerate(INVESTMENT_HEADERS):
            data = lookup_attr(item, INVESTMENT_EXPORT_COLUMNS[key])
            if key == "AMOUNT":
                ws.write(i+1, j, int(data), style=currency_style)
            elif key.startswith("CONTRIBUTED"):
                ws.write(i+1, j, data, style=date_style)
            elif key.startswith("COMPLETED"):
                ws.write(i+1, j, data, style=date_style)
            else:
                ws.write(i+1, j, data)

    wb.save(response)

    return response


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
