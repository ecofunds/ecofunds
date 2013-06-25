from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from ecofunds.opportunity import models

class CMSFundingOpportunitiesPlugin(CMSPluginBase):
    """
        Plugin class for the latest news
    """
    model = models.FundingOpportunityPlugin
    name = _('Funding Opportunity List')
    render_template = "opportunity/list.html"
    module = _('Funding Opportunity')
    
    def render(self, context, instance, placeholder):
        """
            Render the latest news
        """
        latest = models.FundingOpportunity.published.all()[:instance.limit]
        context.update({
            'instance': instance,
            'latest': latest,
            'placeholder': placeholder,
        })
        return context

class CMSLatestFundingOpportunityPlugin(CMSPluginBase):
    """
        Plugin class for the latest news
    """
    model = models.FundingOpportunityPlugin
    name = _('Latest Funding Opportunity')
    render_template = "opportunity/latest.html"
    module = _('Funding Opportunity')
    
    def render(self, context, instance, placeholder):
        """
            Render the latest news
        """
        latest = models.FundingOpportunity.published.all()[:instance.limit]
        context.update({
            'instance': instance,
            'latest': latest,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSFundingOpportunitiesPlugin)
plugin_pool.register_plugin(CMSLatestFundingOpportunityPlugin)