from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.utils.simplejson import dumps
import tablib
from babel import numbers
from aggregate_if import Count

from ecofunds.core.models import Organization, ProjectLocation, Project, Investment
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
    'NAME': 'title',
    'ACRONYM': 'acronym',
    'ACTIVITY_TYPE': 'activity_description',
    'DESCRIPTION': 'description',
    'URL': 'website',
    'EMAIL': 'email',
    'PHONE': 'formated_phone_number',
    'LAT': 'lat',
    'LNG': 'lng'
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

    qs = ProjectLocation.objects.search(**form.cleaned_data)

    if map_type == "csv":
        return output_project_csv(qs)
    elif map_type == "xls":
        return output_project_excel(qs)
    else:
        return output_project_json(qs)


def output_project_json(qs):
    points = {}
    for obj in qs:
        marker = {
            'entity_id': obj.entity.pk,
            'location_id': obj.location.pk,
            'lat': obj.entity.lat,
            'lng': obj.entity.lng,
            'acronym': obj.entity.title,
            'url': obj.entity.website,
        }
        points[obj.entity.pk] = marker

    gmap = {}
    gmap['items'] = points.values()

    return HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


def output_project_csv(qs):
    data = tablib.Dataset(PROJECT_HEADERS)
    for item in qs:
        row = []
        for key in PROJECT_HEADERS:
            row.append(getattr(item.entity, PROJECT_EXPORT_COLUMNS[key]))
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
            data = getattr(item.entity, PROJECT_EXPORT_COLUMNS[key])
            if data and isinstance(data, unicode) and len(data) > 3000:
                data = data[:3000]
            ws.write(i+1, j, data)

    wb.save(response)

    from django.db import connection
    print connection.queries

    return response


def investment_api(request, map_type):
    if map_type not in ("density"):
        return HttpResponseBadRequest()

    form = InvestmentFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = ProjectLocation.objects.search_investment(**form.cleaned_data)
    qs = qs.only('location__centroid', 'entity__title', 'entity__website')

    points = {}

    for obj in qs:
        project = {
            'id': obj.entity.pk, # Should be investment ID, but it's not possible
            'acronym': obj.entity.title,
            'url': obj.entity.website,
            'entity_id': obj.entity.pk,
            'amount': float(obj.entity_amount),
            'amount_str': format_currency(obj.entity_amount)
        }

        if not obj.location.pk in points:
            lat, lng = parse_centroid(obj.location.centroid)

            points[obj.location.pk] = {
                'location_id': obj.location.pk,
                'lat': lat,
                'lng': lng,
                'total_investment': float(obj.entity_amount),
                'total_investment_str': format_currency(obj.entity_amount),
                'projects': [project]
            }
        else:
            points[obj.location.pk]['projects'].append(project)
            points[obj.location.pk]['total_investment'] += float(obj.entity_amount)
            points[obj.location.pk]['total_investment_str'] = format_currency(points[obj.location.pk]['total_investment'])

    gmap = {}
    gmap['items'] = points.values()

    return HttpResponse(dumps(dict(map=gmap)), content_type="application/json")


ORGANIZATION_EXPORT_COLUMNS = {
    'NAME': 'name',
    'DESCRIPTION': 'mission',
    'ORG. TYPE': 'kind',
    'ADDRESS': 'street1',
    'ZIPCODE': 'zip',
    'EMAIL': 'email',
    'URL':  'url',
    'PHONE': 'formated_phone_number',
    'LOCATION': 'location_name',
    'LAT': 'desired_location_lat',
    'LNG': 'desired_location_lng',
}


ORGANIZATION_HEADERS = ['NAME', 'DESCRIPTION', 'ORG. TYPE', 'ADDRESS', 'ZIPCODE',
                        'EMAIL', 'URL' , 'PHONE',  'LOCATION' , 'LAT', 'LNG']


def organization_api(request, map_type):
    if map_type not in ("marker", "csv", "xls"):
        return HttpResponseBadRequest()

    form = OrganizationFilterForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    qs = Organization.objects.search(**form.cleaned_data).select_related('type', 'location')

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
            'name': obj.name.encode('utf-8'),
            'lat': float(str(obj.desired_location_lat)),
            'lng': float(str(obj.desired_location_lng)),
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
            row.append(getattr(item, ORGANIZATION_EXPORT_COLUMNS[key]))
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
            ws.write(i+1, j, getattr(item, ORGANIZATION_EXPORT_COLUMNS[key]))

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
