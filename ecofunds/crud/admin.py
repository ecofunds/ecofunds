# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext as _
from django import forms
from suit.widgets import AutosizedTextarea

from models import *

from ecofunds.geonames.models import Geoname
from django_select2 import AutoModelSelect2Field, AutoHeavySelect2Widget


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name',)


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
    search_fields = ['name__icontains', ]

    def get_results(self, request, term, page, context):
        try:
            data = Geoname.objects.filter(name__icontains=term).order_by('country')
            data = map(lambda x: (x.geonameid, unicode(x)), data)
            return ('nil', False, data)
        except Exception as e:
            #TODO LOG
            return (e, false, [])


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
class ProjectChoices(AutoModelSelect2Field):
    queryset = Project2.objects.all()
    search_fields = ['name__icontains', 'acronym__icontains']


class OrganizationChoices(AutoModelSelect2Field):
    queryset = Organization2.objects.all()
    search_fields = ['name__icontains', 'acronym__icontains']


class InvestmentForm(forms.ModelForm):
    funding_organization = OrganizationChoices()
    funding_project = ProjectChoices()
    recipient_organization = OrganizationChoices()
    recipient_project = ProjectChoices()

    class Meta:
        model = Investment2


class InvestmentAdmin(admin.ModelAdmin):
    form = InvestmentForm
    list_display = ('funding_organization', 'funding_project', 'amount', 'contributed_at',
                    'recipient_organization', 'recipient_project')
    list_filter = ('amount', 'contributed_at')


admin.site.register(Organization2, OrganizationAdmin)
admin.site.register(Project2, ProjectAdmin)
admin.site.register(Investment2, InvestmentAdmin)
admin.site.register(Activity2, ActivityAdmin)
