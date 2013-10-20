from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.simplejson import dumps

from ecofunds.crud.models import Organization2, Project2, Investment2

def project_detail(request, project_id):
    model = get_object_or_404(Project2, id=project_id)
    return render(request, "project/new_detail.html", {'project': model})

def investment_detail(request, investment_id):
    model = get_object_or_404(Investment2, id=investment_id)
    return render(request, "investment/new_detail.html", {'investment': model})

def organization_detail(request, organization_id):
    model = get_object_or_404(Organization2, id=organization_id)
    return render(request, "organization/new_detail.html", {'organization': model})

# REPEATED CODE
# THIS NEW VERSION IS ADAPTED FOR THE NEW MODELS

def output_project_json(qs):
    points = {}
    for obj in qs:
        marker = {
            'entity_id': obj.pk,
            'location_id': obj.location.geonameid,
            'lat': obj.location.latitude,
            'lng': obj.location.longitude,
            'acronym': obj.acronym,
            'name': obj.name,
            'url': obj.url,
        }
        points[obj.pk] = marker

    gmap = {}
    gmap['items'] = points.values()

    return HttpResponse(dumps(dict(map=gmap)), content_type="application/json")

def output_organization_json(qs):
    points = {}

    for obj in qs:
        try:
            marker = {
                'entity_id': obj.pk,
                'name': obj.name,
                'acronym': obj.acronym,
                'lat': obj.location.latitude,
                'lng': obj.location.longitude,
            }
            points[obj.pk] = marker
        except Exception as e:
            print(e)
            points[obj.pk] = dict(erro="Incomplete Data on Database")

    gmap = {}
    gmap['items'] = points.values()

    return HttpResponse(dumps(dict(map=gmap)), content_type="application/json")

#END REPEATED CODE

def project_detail_json(request, project_id):
    qs = Project2.objects.filter(id=project_id).exclude(location=None)
    return output_project_json(qs)

def organization_detail_json(request, organization_id):
    qs = Organization2.objects.filter(id=organization_id)
    return output_organization_json(qs)

def investment_detail_json(request, investment_id):
    qs = Investment2.objects.filter(id=project_id)
    raise Exception("Not Implemented")
