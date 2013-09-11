# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext as _
from models import Project, Organization, Investment, Activity


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


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'kind', 'start_at')
    list_filter = ('start_at', 'kind')
    search_fields = ('name', 'acronym')
    fieldsets = (
            (None, {
                'fields': ('name', 'acronym', 'kind', 'organization', 'description', 'start_at', 'end_at', 'goal', 'activities', 'geofocus')
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


class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('funding_organization', 'funding_project', 'amount', 'contributed_at',
                    'recipient_organization', 'recipient_project')
    list_filter = ('amount', 'contributed_at')


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(Activity)
