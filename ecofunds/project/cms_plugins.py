from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.shortcuts import get_object_or_404

from django.utils.translation import ugettext_lazy as _
from ecofunds.core.models import Project
from ecofunds.project.models import DetailProjectPlugin
from ecofunds.user.models import UserProfile
from ecofunds.user.permissions import edit_allowance


class CMSDetailProjectPlugin(CMSPluginBase):
    model = DetailProjectPlugin
    name = _("Project Detail")
    render_template = "project/detail.html"
    module = _("Project")

    def render(self, context, instance, placeholder):
        request = context['request']
        id = request.GET.get('id')
        page = request.GET.get('page')

        project = get_object_or_404(Project, pk=id)
        perm = False
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except UserProfile.DoesNotExist:
                profile = None
            if profile:
                perm = edit_allowance(project,profile)
        if project:
            locations = [pl.location.id for pl in project.projects_locations.all()]
            activities = [pa.activity_id for pa in project.projects_activities.all()]
        else:
            locations = []
            activities = []


        context.update({
            'project':project,
            'attachments': (),
            'similar_location_projects': Project.objects.filter(projects_locations__location_id__in=locations).exclude(pk=id)[:5],
            'similar_activity_projects': Project.objects.filter(projects_activities__activity_id__in=activities).exclude(pk=id)[:5],
            'instance':instance,
            'placeholder':placeholder,
            'perm':perm,
        })
        return context

plugin_pool.register_plugin(CMSDetailProjectPlugin)
