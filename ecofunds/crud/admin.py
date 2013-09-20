# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext as _
from django import forms
from suit.widgets import AutosizedTextarea

from models import *

from ecofunds.geonames.models import Geoname
from django_select2 import AutoModelSelect2Field, AutoHeavySelect2Widget


# Organization Admin

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'kind',)
    search_fields = ('name', 'acronym', 'kind',)
    list_filter = ('kind',)
    fieldsets = (
        (None, {
            'fields': ('name', 'acronym', 'kind', 'description', 'director',)
        }),
        (_(u'Contact'), {
            'classes': ('wide',),
            'fields': ('url', 'email', 'phone', 'fax',)
        }),
        (_(u'Address'), {
            'classes': ('wide',),
            'fields': ('address', 'zipcode', 'city', 'state', 'country',)
        }),
        (_(u'Centroid'), {
            'classes': ('wide',),
            'fields': ('lat', 'lng',),
        }),
    )


# Project Admin

class CountryChoices(AutoModelSelect2Field):
    queryset = Geoname.objects
    search_fields = ['name__istartswith', ]


class ProjectForm(forms.ModelForm):
    location = CountryChoices(widget=AutoHeavySelect2Widget)
    class Meta:
        model = Project2
        widgets = {
            'description': AutosizedTextarea(attrs={'class': 'vLargeTextField', 'rows': 4}),
            'goal': AutosizedTextarea(attrs={'class': 'vLargeTextField'}),
            'geofocus': AutosizedTextarea(attrs={'class': 'vLargeTextField'}),
        }


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    list_display = ('name', 'acronym', 'kind', 'start_at')
    list_filter = ('start_at', 'kind')
    search_fields = ('name', 'acronym')
    fieldsets = (
            (None, {
                'fields': ('name', 'acronym', 'kind', 'organization', 'description',
                           'start_at', 'end_at', 'goal', 'activities', 'geofocus',
                           'location')
            }),
            (_(u'Contact'), {
                'classes': ('wide',),
                'fields': ('url', 'email', 'phone', 'fax',)
            }),
            (_(u'Address'), {
                'classes': ('wide',),
                'fields': ('address', 'zipcode', 'city', 'state', 'country',)
            }),
            (_(u'Centroid'), {
                'classes': ('wide',),
                'fields': ('lat', 'lng',),
            }),
        )


# Investment Admin

class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('funding_organization', 'funding_project', 'amount', 'contributed_at',
                    'recipient_organization', 'recipient_project')
    list_filter = ('amount', 'contributed_at')


admin.site.register(Organization2, OrganizationAdmin)
admin.site.register(Project2, ProjectAdmin)
admin.site.register(Investment2, InvestmentAdmin)
admin.site.register(Activity2)
