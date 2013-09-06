from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.shortcuts import get_object_or_404

from django.utils.translation import ugettext_lazy as _
from ecofunds.core.models import Investment
from ecofunds.user.models import UserProfile

from ecofunds.user.permissions import edit_allowance


class CMSDetailInvestmentPlugin(CMSPluginBase):
    name = _("Investment Detail")
    render_template = "investment/detail.html"
    module = _("Investment")

    def render(self, context, instance, placeholder):
        request = context['request']
        id = request.GET.get('id')
        page = request.GET.get('page')
        investment = get_object_or_404(Investment, pk=id)
        perm = False
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except UserProfile.DoesNotExist:
                profile = None
            if profile:
                perm = edit_allowance(investment,profile)
        context.update({
            'investment': investment,
            'attachments': (),
            'highest_investments': Investment.objects.exclude(pk=id).order_by('-amount_usd')[:3],
            'similar_investment_types': Investment.objects.filter(type_id__exact=investment.type_id).exclude(pk=id)[:3],
            'instance':instance,
            'placeholder':placeholder,
            'perm':perm,
        })
        return context

plugin_pool.register_plugin(CMSDetailInvestmentPlugin)
