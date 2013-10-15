from django.shortcuts import render
from django.shortcuts import render_to_response, redirect, get_object_or_404

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
