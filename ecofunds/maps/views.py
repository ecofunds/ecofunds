from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.utils.simplejson import dumps
import tablib
from babel import numbers
from ecofunds.crud.models import Organization2

from ecofunds.core.models import Organization, ProjectLocation, Project, Investment
from ecofunds.crud.models import Project2, Organization2, Investment2
from ecofunds.crud.forms import OrganizationFilterForm, ProjectFilterForm, InvestmentFilterForm
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
        'entity_id': obj.pk,
        'lat': obj.location.latitude,
        'lng': obj.location.longitude,
        'acronym': obj.name,
        'url': obj.url
    }

def output_project_json(qs):
    points = {}
    for obj in qs:
        points[obj.pk] = project_marker(obj)

    gmap = {}
    gmap['items'] = points.values()

    return HttpResponse(dumps(dict(map=gmap)), content_type="application/json")

def lookup_attr(obj, lookup):
    attr, sep, tail_lookup = lookup.partition('__')

    value = getattr(obj, attr)
    if tail_lookup:
        return lookup_attr(value, tail_lookup)
    else:
        return value


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
            data = lookup_attr(item.entity, PROJECT_EXPORT_COLUMNS[key])
            if data and isinstance(data, unicode) and len(data) > 3000:
                data = data[:3000]
            ws.write(i+1, j, data)

    wb.save(response)

    return response


INVESTMENT_EXPORT_COLUMNS = {
    'ACRONYM': 'acronym',
    'LOCATION': 'location',
    'COUNTRY': 'country',
    'LAT': 'lat',
    'LNG': 'lng',
    'AMOUNT': 'amount',
}

INVESTMENT_HEADERS = ['ACRONYM', 'COUNTRY', 'LOCATION', 'LAT', 'LNG', 'AMOUNT']

def investment_api(request, map_type):
    if map_type not in ("density", "csv", "xls"):
        return HttpResponseBadRequest()

    form = InvestmentFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Investment2.objects.search(**form.cleaned_data)
    #qs = qs.only('location__centroid', 'entity__title', 'entity__website')
    #qs = qs.order_by('location__country__name', 'location__name')

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
                project['recipient_project_id'] = project_marker(obj.recipient_project)

            if obj.funding_project:
                project['funding_project_id'] = project_marker(obj.funding_project)

            if not obj.recipient_project.location.pk in points:
                points[obj.recipient_project.location.pk] = {
                    'location': obj.recipient_project.location.name,
                    'location_id': obj.recipient_project.location.pk,
                    'lat': obj.recipient_project.location.latitude,
                    'lng': obj.recipient_project.location.longitude,
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
            lat, lng = parse_centroid(obj.location.centroid)
            project = {
                'id': obj.entity.pk, # Should be investment ID, but it's not possible
                'acronym': obj.entity.title,
                'url': obj.entity.website,
                'entity_id': obj.entity.pk,
                'amount': float(obj.entity_amount),
                'location': obj.location.name,
                'country': obj.location.country.name,
                'location_id': obj.location.pk,
                'lat': lat,
                'lng': lng,
            }
            items.append(project)

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
            row.append(item[INVESTMENT_EXPORT_COLUMNS[key]])
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
    currency_style.num_format_str = "[$$-409]#,##0.00;-[$$-409]#,##0.00"

    for i, header in enumerate(INVESTMENT_HEADERS):
        ws.write(0, i, header)

    for i, item in enumerate(items):
        row = []
        for j, key in enumerate(INVESTMENT_HEADERS):
            data = item[INVESTMENT_EXPORT_COLUMNS[key]]
            if key == "AMOUNT":
                ws.write(i+1, j, data, style=currency_style)
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
            'entity_id': obj.pk,
            'name': obj.name,
            'acronym': obj.acronym,
            'lat': obj.location.latitude,
            'lng': obj.location.longitude,
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
