from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.core.cache import cache
from django.db.models import Count
from django.db import IntegrityError
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from ecofunds import settings
from ecofunds.models import *
from ecofunds.user.models import UserProfile
from ecofunds.user.notification import notificate
from ecofunds.project.models import *
from ecofunds.project.forms import *
from ecofunds.business import *
from ecofunds.views import item_permission_list
from ecofunds.cms_plugins import GenericCMSFormPlugin
from ecofunds.user.permissions import edit_allowance

from gmapi import maps
from gmapi.maps import Geocoder
from ecofunds.middleware.forcedresponse import ForceResponse

import pygeoip

class CMSProjectsPlugin(CMSPluginBase):
    model = ProjectsPlugin
    name = _("Project List")
    render_template = "project/list.html"
    module = _("Project")

    def render(self, context, instance, placeholder):
        request = context['request']
        data = request.POST if request.method == "POST" else request.GET
        limit = instance.table_limit if data.get('list_type') == 2 else instance.card_limit
        list, form, labels = ProjectData.filteredList(request, limit)
        itempermlist = item_permission_list(request,list)
        context.update({
            'itempermlist':itempermlist,
            'list':list,
            'labels':labels,
            'latest_projects': ProjectData.list()[:5],
            'latest_investments': InvestmentData.list()[:5],

            'count_projects': ProjectData.list().count,
            'count_project_activity_types': Activity.objects.count,
            'count_project_regions': Project.objects.values('projects_locations__location__name').annotate(total=Count('projects_locations__location__name')).count,
            'count_organizations': Organization.objects.count,
            'count_investments': Investment.objects.values('recipient_entity').annotate(total=Count('recipient_entity')).count,

            'search_project_form':form,
            'page_detail':instance.page_detail,
            'instance':instance,
            'placeholder':placeholder
        })
        return context

class CMSSearchProjectPlugin(CMSPluginBase):
    model = SearchProjectPlugin
    name = _("Search Projects")
    render_template = "project/search.html"
    module = _("Project")

    def render(self, context, instance, placeholder):
        request = context['request']
        if request.method == "POST":
            form = ProjectAdvancedSearchForm(request.POST)
        else:
            form = ProjectAdvancedSearchForm()

        context.update({
            'search_project_form': form,
            'page_result':instance.page_result,
            'instance':instance,
            'placeholder':placeholder
        })
        return context

class CMSCarouselProjectPlugin(CMSPluginBase):
    model = ProjectsPlugin
    name = _("Carousel Project")
    render_template = "project/carousel.html"
    module = _("Project")

    def render(self, context, instance, placeholder):
        request = context['request']
        page = request.GET.get('page')
        list = ProjectData.paginatedList(instance.card_limit, page)

        context.update({
            'list':list,
            'instance':instance,
            'page_detail':instance.page_detail,
            'placeholder':placeholder
        })
        return context

class CMSLatestProjectsPlugin(CMSPluginBase):
    """
    Plugin class for the latest projects
    """
    model = ProjectsPlugin
    name = _("Latest Projects")
    render_template = "project/latest.html"
    module = _("Project")

    def render(self, context, instance, placeholder):
        request = context['request']
        page = request.GET.get('page')
        list = ProjectData.paginatedList(instance.card_limit, page)

        context.update({
            'list':list,
            'instance':instance,
            'placeholder':placeholder
        })
        return context

class CMSDetailProjectPlugin(CMSPluginBase):
    model = DetailProjectPlugin
    name = _("Project Detail")
    render_template = "project/detail.html"
    module = _("Project")

    def render(self, context, instance, placeholder):
        request = context['request']
        id = request.GET.get('id')
        page = request.GET.get('page')

        project = ProjectData.item(id)
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
            'attachments':ProjectData.paginatedAttachmentList(id, 5, page),
            'similar_location_projects':ProjectData.list(projects_locations__location_id__in=locations).exclude(pk=id)[:5],
            'similar_activity_projects':ProjectData.list(projects_activities__activity_id__in=activities).exclude(pk=id)[:5],
            'instance':instance,
            'placeholder':placeholder,
            'perm':perm,
        })
        return context


class CMSFormProjectPlugin(GenericCMSFormPlugin):
    model = ProjectFormPlugin
    name = _("Project Form")
    render_template =  "project/form.html"
    module = _("Project")
    DjangoModel = Project
    DjangoForm = ProjectForm

    redirect_language = {'pt-br':'../ficha-projeto',
            'en':'../project-detail',
            'es':'../project-detail',
            }

    def render(self,context,instance,placeholder):
        request = context['request']
        if request.method=='POST':
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    proj = self.DjangoModel.objects.get(pk=pk_id)
                    projform = self.DjangoForm(request.POST,request.FILES,instance=proj)
                    note_type="update"
                    projform.updater=request.user
                except self.DjangoModel.DoesNotExist:
                    projform = self.DjangoForm(request.POST,request.FILES)
                    projform.creater = request.user
            else:
                projform = self.DjangoForm(request.POST,request.FILES)
                note_type="create"
            if projform.is_valid():
                p=projform.save(commit=False)
                p.creater = request.user
                if projform.cleaned_data.get('category')=='True':
                    p.is_project = True
                p.save()
                if projform.cleaned_data.get('organization'):
                    for org in projform.cleaned_data.get('organization'):
                        obj = Organization.objects.get(pk=org)
                        pjorg=ProjectOrganization(entity=p,organization=obj)
                        if org == projform.cleaned_data.get('main_org'):
                            pjorg.main=True
                        try:
                            pjorg.save()
                        except IntegrityError:
                            pjorg = ProjectOrganization.objects.get(entity=p,organization=obj)
                            if org == projform.cleaned_data.get('main_org'):
                                pjorg.main = True
                                pjorg.save()
                if projform.cleaned_data.get('activities'):
                    for act in projform.cleaned_data.get('activities'):
                        obj = Activity.objects.get(pk=act)
                        pjact = ProjectActivity(entity=p,activity=obj)
                        try:
                            pjact.save()
                        except IntegrityError:
                            pass
                if projform.cleaned_data.get('locations'):
                    for loc in projform.cleaned_data.get('locations'):
                        obj = Location.objects.get(pk=loc)
                        pjloc = ProjectLocation(entity=p,location=obj)
                        try:
                            pjloc.save()
                        except IntegrityError:
                            pass
                if projform.cleaned_data.get('child_projects'):
                    for subp  in projform.cleaned_data.get('child_projects'):
                        obj = Project.objects.get(pk=subp)
                        pxp = ProjectXProject(parent_project=p,child_project=obj)
                        try:
                            pxp.save()
                        except IntegrityError:
                            pass
                if projform.cleaned_data.get('father_projects'):
                    for subp  in projform.cleaned_data.get('child_projects'):
                        obj = Project.objects.get(pk=subp)
                        pxp = ProjectXProject(child_project=p,parent_project=obj)
                        try:
                            pxp.save()
                        except IntegrityError:
                            pass
                notificate(p,note_type,request.user,'teste')
                context.update({'redirect':p.pk})
                lang = get_language()
                redirect_url = self.redirect_language[lang]
                raise ForceResponse(HttpResponseRedirect(redirect_url+'?id=%s'%p.pk))
            else:
                print projform.errors
                context.update({'formset':projform})
                return context
        else:
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    proj = self.DjangoModel.objects.get(pk=pk_id)
                except self.DjangoModel.DoesNotExist:
                    context.update({'formset':self.DjangoForm()})
                    return context
                context.update({'formset':self.DjangoForm(instance=proj)})
                return context
            else:
                context.update({'formset':self.DjangoForm() })
                return context

plugin_pool.register_plugin(CMSDetailProjectPlugin)
plugin_pool.register_plugin(CMSSearchProjectPlugin)
plugin_pool.register_plugin(CMSProjectsPlugin)
plugin_pool.register_plugin(CMSLatestProjectsPlugin)
plugin_pool.register_plugin(CMSCarouselProjectPlugin)
plugin_pool.register_plugin(CMSFormProjectPlugin)
