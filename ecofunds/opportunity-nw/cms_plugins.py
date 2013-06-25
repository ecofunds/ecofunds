from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.core.cache import cache
from django.db.models import Count
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _

from ecofunds import settings
from ecofunds.models import *
from ecofunds.business import *
from ecofunds.opportunity.forms import *
from ecofunds.opportunity.models import *

from gmapi import maps
from gmapi.maps import Geocoder

import pygeoip

class CMSFundingOpportunitiesPlugin(CMSPluginBase):
    model = OpportunityPlugin
    name = _("Opportunity List")
    render_template = "opportunity/list.html"
    module = _("Opportunity")

    def render(self, context, instance, placeholder):
        request = context['request']

        list, form, labels = OpportunityData.filteredList(request, instance.limit)

        context.update({
            'list':list,
            'labels':labels,
            'search_opportunity_form':form,
            'page_detail':instance.page_detail,
            'instance':instance,
            'placeholder':placeholder
        })
        return context

class CMSLatestFundingOpportunityPlugin(CMSPluginBase):

    model = OpportunityPlugin
    name = _("Latest Opportunities")
    render_template = "opportunity/latest.html"
    module = _("Opportunity")

    def render(self, context, instance, placeholder):
        request = context['request']
        page = request.GET.get('page')
        list = OpportunityData.paginatedList(instance.limit, page)

        context.update({
            'list':list,
            'instance':instance,
            'placeholder':placeholder
        })
        return context

class CMSDetailOpportunityPlugin(CMSPluginBase):
    model = DetailOpportunityPlugin
    name = _("Opportunity Detail")
    render_template = "opportunity/detail.html"
    module = _("Opportunity")

    def render(self, context, instance, placeholder):
        request = context['request']
        id = request.GET.get('id')
        opportunity = OpportunityData.item(id)
        activities = []
        for po in opportunity.projects_opportunities.all():
            for pa in po.entity.projects_activities.all():
                activities.append(pa.activity.id)

        context.update({
            'opportunity': opportunity,
            'instance':instance,
            'placeholder':placeholder
        })
        return context

plugin_pool.register_plugin(CMSOpportunityPlugin)
plugin_pool.register_plugin(CMSLatestOpportunitiesPlugin)
plugin_pool.register_plugin(CMSDetailOpportunityPlugin)