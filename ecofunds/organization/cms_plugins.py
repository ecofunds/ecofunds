from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.shortcuts import get_object_or_404

from django.utils.translation import ugettext_lazy as _
from ecofunds.core.models import Organization
from ecofunds.organization.models import DetailOrganizationPlugin
from ecofunds.user.models import UserProfile

from ecofunds.user.permissions import edit_allowance


class CMSDetailOrganizationPlugin(CMSPluginBase):
    model = DetailOrganizationPlugin
    name = _("Organization Detail")
    render_template = "organization/detail.html"
    module = _("Organization")

    def render(self, context, instance, placeholder):
        request = context['request']
        id = request.GET.get('id')
        organization = get_object_or_404(Organization, pk=id)
        perm = False
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except UserProfile.DoesNotExist:
                profile = None
            if profile:
                perm = edit_allowance(organization,profile)
        activities = []
        for po in organization.projects_organizations.all():
            for pa in po.entity.projects_activities.all():
                activities.append(pa.activity.pk)

        context.update({
            'organization': organization,
            'similar_location_organizations': Organization.objects.filter(country_id=organization.country_id).exclude(pk=id)[:5],
            'similar_activity_organizations': Organization.objects.filter(projects_organizations__entity__projects_activities__activity_id__in=activities).exclude(pk=id)[:5],
            'instance':instance,
            'placeholder':placeholder,
            'perm':perm,
        })
        return context

plugin_pool.register_plugin(CMSDetailOrganizationPlugin)
