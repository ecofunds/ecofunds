from django.shortcuts import render
from django.shortcuts import render_to_response, redirect, get_object_or_404

from ecofunds.crud.models import Organization2, Project2, Investment2

def project_detail(request, project_id):
    model = get_object_or_404(Project2, id=project_id)
    return render(request, "project/new_detail.html", {'project':model})

def investment_detail(request, investment_id):
    pass

def organization_detail(request, organization_id):
    pass
