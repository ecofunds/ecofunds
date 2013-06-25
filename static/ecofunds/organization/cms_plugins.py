from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.core.cache import cache
from django.db.models import Count
from django.db import IntegrityError
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.utils.translation import get_language

from ecofunds import settings
from ecofunds.models import *
from ecofunds.user.models import *
from ecofunds.user.notification import notificate
from ecofunds.business import *
from ecofunds.organization.forms import *
from ecofunds.organization.models import *
from ecofunds.views import item_permission_list
from ecofunds.cms_plugins import GenericCMSFormPlugin
from ecofunds.user.permissions import edit_allowance

from gmapi import maps
from gmapi.maps import Geocoder
from ecofunds.middleware.forcedresponse import ForceResponse

from datetime import datetime
import pygeoip

class CMSOrganizationPlugin(CMSPluginBase):
    model = OrganizationPlugin
    name = _("Organization List")
    render_template = "organization/list.html"
    module = _("Organization")

    def render(self, context, instance, placeholder):
        request = context['request']

        list, form, labels = OrganizationData.filteredList(request, instance.limit)

        itempermlist = item_permission_list(request,list)
        context.update({
            'itempermlist':itempermlist,
            'list':list,
            'labels':labels,
            'search_organization_form':form,
            'count_project_activity_types': Activity.objects.count,
            'count_organizations': Organization.objects.count,
            'count_organization_types': OrganizationType.objects.count,
            'count_organization_regions': Organization.objects.values('state').annotate(total=Count('state')).count,
            'count_organization_investments': Investment.objects.values('funding_organization').annotate(total=Count('funding_organization')).count,
            'count_recipient_organization': Investment.objects.values('recipient_organization').annotate(total=Count('recipient_organization')).count,

            'page_detail':instance.page_detail,
            'instance':instance,
            'placeholder':placeholder
        })
        if len(list.object_list) == 0:

            cur = db.connection.cursor()
            sql = """
select o.id, o.name, o.mission
from ecofunds_organization o
join ecofunds_investments i on i.recipient_organization_id = o.id
group by o.id, o.name, o.mission
order by i.created_at desc
limit 5
"""
            cur.execute(sql)
            items = cur.fetchall()
            latest = []
            for x in items:
                item = Organization()
                item.id = x[0]
                item.name = x[1]
                item.mission = x[2]
                latest.append(item)            
                        
            context.update({
                            'new_organizations': OrganizationData.list()[:5], 
                            'latest_investment_organizations': latest
            })

        return context

class CMSLatestOrganizationsPlugin(CMSPluginBase):

    model = OrganizationPlugin
    name = _("Latest Organizations")
    render_template = "organization/latest.html"
    module = _("Organization")

    def render(self, context, instance, placeholder):
        request = context['request']
        page = request.GET.get('page')
        list = OrganizationData.paginatedList(instance.limit, page)

        context.update({
            'list':list,
            'instance':instance,
            'placeholder':placeholder
        })
        return context

class CMSDetailOrganizationPlugin(CMSPluginBase):
    model = DetailOrganizationPlugin
    name = _("Organization Detail")
    render_template = "organization/detail.html"
    module = _("Organization")

    def render(self, context, instance, placeholder):
        request = context['request']
        id = request.GET.get('id')
        organization = OrganizationData.item(id)
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
            'similar_location_organizations':OrganizationData.list(country_id=organization.country_id).exclude(pk=id)[:5],
            'similar_activity_organizations':OrganizationData.list(projects_organizations__entity__projects_activities__activity_id__in=activities).exclude(pk=id)[:5],
            'instance':instance,
            'placeholder':placeholder,
            'perm':perm,
        })
        return context

class CMSPFormOrganizationPlugin(GenericCMSFormPlugin):
    model = OrganizationFormPlugin
    name = _("Organization Form")
    render_template = "organization/form.html"
    module = _("Organization")
    DjangoModel = Organization
    DjangoForm = OrganizationForm
 
    redirect_language = {'pt-br':'../ficha-organizacao',
            'en':'../organization-detail',
            'es':'../ficha-organizacion',
            }

    def render(self,context,instance,placeholder):
        request = context['request']
        if request.method=='POST':
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    proj = self.DjangoModel.objects.get(pk=pk_id)
                    projform = self.DjangoForm(request.POST,request.FILES,instance=proj)
                    note_type = 'update'
                except self.DjangoModel.DoesNotExist:
                    projform = self.DjangoForm(request.POST,request.FILES)
            else:
                projform = self.DjangoForm(request.POST,request.FILES)
                note_type='create'
            if projform.is_valid():
                ceo = projform.cleaned_data.get('ceo')
                ceo = ceo.split(" ")
                first = ceo[0]
                if len(ceo)>1:
                    last = ceo[1]
                else:
                    last = ""
                p=projform.save(commit=False)
                if note_type=='create':
                    p.created_at = datetime.now()
                    p.creater = request.user
                elif note_type=='updated':
                    p.updated_at = datetime.now()
                    p.updater = request.user
                p.contact_first_name=first
                p.contact_last_name=last
                p.save()
                if projform.cleaned_data.get('connections'):
                    for profile in projform.cleaned_data.get('connections'):
                        obj = UserProfile.objects.get(pk=profile)
                        userorg = UserProfileOrganization(userprofile=obj,
                                organization=p,admin=True)
                        try:
                            userorg.save()
                        except IntegrityError:
                            pass
                if projform.cleaned_data.get('projects'):
                    for act in projform.cleaned_data.get('projects'):
                        obj = Project.objects.get(pk=act)
                        pjorg =ProjectOrganization(organization=p,entity=obj)
                        try:
                            pjorg.save()
                        except IntegrityError:
                            pass
                admin=False
                if projform.cleaned_data.get('admin')=='True':
                    admin=True
                prof = request.user.get_profile()
                if not UserProfileOrganization.objects.filter(userprofile=prof,organization=p):
                    UserProfileOrganization(userprofile=prof,
                        organization=p,admin=admin).save()
                    if prof.user_type.name=='regularuser':
                        orgadmintype=UserType.objects.get(name='organizationadmin')
                        prof.user_type = orgadmintype
                        prof.save()
                else:
                    upo = UserProfileOrganization.objects.get(userprofile=prof,organization=p)
                    upo.admin=admin
                    upo.save()
                #notifica no final
                notificate(p,note_type,request.user,'notificacao')
                context.update({'redirect':p.pk})
                lang = get_language()
                redirect_url = self.redirect_language[lang]
                raise ForceResponse(HttpResponseRedirect(redirect_url+'?id=%s'%p.pk))
            else:
                context.update({'formset':projform})
                return context
        else:
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    proj = self.DjangoModel.objects.get(pk=pk_id)
                except self.DjangoModel.DoesNotExist:
                    context.update({'formset':self.DjangoForm() })
                    return context
                ceo_init = proj.contact_first_name +' '+ proj.contact_last_name
                profile = request.user.get_profile()
                admin_init = 'False'
                if UserProfileOrganization.objects.filter(userprofile=profile,organization=proj,admin=True):
                    admin_init = 'True'
                formedit = self.DjangoForm(instance=proj,initial = {'ceo':ceo_init,'admin':admin_init})
                context.update({'formset':formedit})
                return context
            else:
                context.update({'formset':self.DjangoForm() })
                return context

plugin_pool.register_plugin(CMSOrganizationPlugin)
plugin_pool.register_plugin(CMSLatestOrganizationsPlugin)
plugin_pool.register_plugin(CMSDetailOrganizationPlugin)
plugin_pool.register_plugin(CMSPFormOrganizationPlugin)
