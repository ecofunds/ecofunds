from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count

from ecofunds.maps.forms import MapForm
from ecofunds.maps.models import GoogleMapView, GoogleMapPlugin

from ecofunds.project.forms import ProjectAdvancedSearchForm
from ecofunds.organization.forms import OrganizationAdvancedSearchForm
from ecofunds.investment.forms import InvestmentAdvancedSearchForm
from ecofunds.models import *

class CMSGoogleMapPlugin(GoogleMapView, CMSPluginBase):
    name = _('Google Map')
    render_template = "maps/map.html"
    model = GoogleMapPlugin

    def render(self, context, instance, placeholder):

        request = context['request']
        gmap = self.get_map(request)

        if instance.show_search_projects:
            if request.method == "POST":
                search_project_form = ProjectAdvancedSearchForm(request.POST)
            else:
                search_project_form = ProjectAdvancedSearchForm(request.GET)
        else:
            search_project_form = None

        if instance.show_search_organizations:
            if request.method == "POST":
                search_organization_form = OrganizationAdvancedSearchForm(request.POST)
            else:
                search_organization_form = OrganizationAdvancedSearchForm()
        else:
            search_organization_form = None

        if instance.show_search_investments:
            if request.method == "POST":
                search_investment_form = InvestmentAdvancedSearchForm(request.POST)
            else:
                pass
                search_investment_form = InvestmentAdvancedSearchForm()
        else:
            search_investment_form = None

        context.update({
            'form': MapForm(initial={
                'map': gmap,
                'width':instance.width,
                'width_pixels':instance.width_pixels,
                'height':instance.height,
                'height_pixels':instance.height_pixels
            }),
            'search_project_form': search_project_form,
            'search_organization_form': search_organization_form,
            'search_investment_form': search_investment_form,

            
            'count_projects': Project.objects.count,
            'count_project_activity_types': Activity.objects.count,
            'count_project_regions': Project.objects.values('projects_locations__location__name').annotate(total=Count('projects_locations__location__name')).count,
            'count_organizations': Organization.objects.count,
            'count_investments': Investment.objects.values('recipient_entity').annotate(total=Count('recipient_entity')).count,
            'count_organization_types': OrganizationType.objects.count,
            'count_organization_regions': Organization.objects.values('state').annotate(total=Count('state')).count,
            'count_organization_investments': Investment.objects.values('funding_organization').annotate(total=Count('funding_organization')).count,
            'count_recipient_organization': Investment.objects.values('recipient_organization').annotate(total=Count('recipient_organization')).count,
            'instance': instance,
            'placeholder': placeholder,
        })
        return context



class CMSMapLinkPlugin(CMSPluginBase):
    name = _("Map Link")
    render_template = "map-link.html"

    def render(self, context, instance, placeholder):
        return context

plugin_pool.register_plugin(CMSMapLinkPlugin)
plugin_pool.register_plugin(CMSGoogleMapPlugin)
