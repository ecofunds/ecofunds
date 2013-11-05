# coding: utf-8
from django.shortcuts import render, get_object_or_404
from ecofunds.crud.models import Organization2, Project2, Investment2


def project_detail(request, pk):
    obj = get_object_or_404(Project2, id=pk)
    return render(request, "crud/project_detail.html", {'project': obj})


def investment_detail(request, pk):
    obj = get_object_or_404(Investment2, id=pk)
    return render(request, "crud/investment_detail.html", {'investment': obj})


def organization_detail(request, pk):
    obj = get_object_or_404(Organization2, id=pk)
    return render(request, "crud/organization_detail.html", {'organization': obj})
