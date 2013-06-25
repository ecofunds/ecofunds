from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.db.models import Q, Count
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from django.http import Http404

from ecofunds import settings
from ecofunds.models import *
from ecofunds.project.models import *
from ecofunds.business import *
from ecofunds.user.notification import notificate



class CMSSamplingPlugin(CMSPluginBase):
    name = _("Sampling")
    render_template = "sampling.html"
    module = _("Ecofunds")

    def render(self, context, instance, placeholder):
        request = context['request']

        context.update({
            'total_projects': Project.objects.count(),
            'total_organizations': Organization.objects.count(),
            'total_countries': Organization.objects.values('country').annotate(total=Count('country')).count(),
            'instance':instance,
            'placeholder':placeholder
        })

        return context

class CMSListImagePlugin(CMSPluginBase):
    model = ListImagePlugin
    name = _("List Images")
    render_template = "list-images.html"
    
    def render(self, context, instance, placeholder):
        request = context['request']

        context.update({
            'instance':instance,
            'images': instance.images.order_by('position')[:instance.limit],
            'placeholder':placeholder
        })

        return context

class CMSSponsorsPlugin(CMSPluginBase):
    model = ListImagePlugin
    name = _("Sponsors")
    render_template = "sponsors.html"
    module = _("Ecofunds")
    def render(self, context, instance, placeholder):
        request = context['request']

        context.update({
            'instance':instance,
            'images': instance.images.order_by('position')[:instance.limit],
            'placeholder':placeholder
        })

        return context

class CMSGlobalSearchListPlugin(CMSPluginBase):
    name = _("Global Search List")
    render_template = "global-search-result.html"
    module = _("Ecofunds")
    def render(self, context, instance, placeholder):
        request = context['request']
        if request.method == "POST":
            data = request.POST
        else:
            data = request.GET

        search = data.get('query')
        project_page = data.get('project_page')

        projects = None
        organizations = None
        investments = None
        locations = None
        users = None


        order_by = data.get('order_by')
        page = data.get('page')
        
        if not order_by:
            order_by = '-created_at'

        if not page:
            page = 1

        search_type = data.get('search_type')
        
        projects = None
        organizations = None
        investments = None
        locations = None


        if  (search != None and search != ''):
            if not search_type or search_type == 'PRO':
                projects = Paginator(Project.objects.filter(Q(title__icontains=search) | Q(acronym__icontains=search)), 10).page(page)
            if search_type == 'ORG':
                organizations = Paginator(Organization.objects.filter(Q(name__icontains=search) | Q(acronym__icontains=search)), 10).page(page)
            if search_type == 'INV':
                investments = Paginator( InvestmentData.listByQuery(Q(recipient_organization__name__icontains=search) | Q(funding_organization__name__icontains=search)), 10).page(page)
            if search_type == 'LOC':
                query = Location.objects.values('id', 'name','country__name').filter(Q(name__icontains=search)|Q(country__name__icontains=search)).annotate(projects_count=Count('projects__entity_id')).filter(projects_count__gt=1).order_by('name')
                print query.query
                locations = Paginator( query, 10).page(page)

        form = GlobalSearchForm(data)

        context.update({
            'projects': projects,
            'organizations': organizations,
            'investments': investments,
            'locations': locations,
            'users': users,
            'form': form,
            'latest_projects': ProjectData.list()[:5],
            'latest_investments': InvestmentData.list()[:5],

            'instance':instance,
            'placeholder':placeholder

        })

        return context

class GenericCMSFormPlugin(CMSPluginBase):

 
    #FALTA CRIAR AS NOTIFICACOES
    def render(self,context,instance,placeholder):
        request = context['request']
        if request.method=='POST':
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    proj = self.DjangoModel.objects.get(pk=pk_id)
                    projform = self.DjangoForm(request.POST,instance=proj)
                    note_type = 'edit'
                    msg = "User %s edited %s"
                except self.DjangoModel.DoesNotExist:
                    projform = self.DjangoForm(request.POST)
                    projform.creater = request.user
            else:
                projform = self.DjangoForm(request.POST)
                note_type='create'
                msg = "User %s created %s"
            if projform.is_valid():
                p=projform.save()
                notificate(p,note_type,request.user,msg=_("test"))
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
                context.update({'formset':self.DjangoForm(instance=proj)})
                return context
            else:
                context.update({'formset':self.DjangoForm() })
                return context

class CMSAttachments(CMSPluginBase):
    name = _('Attachment')
    render_template = 'attachment.html'
    module = _('Ecofunds')
    model = AttachmentPlugin

    model_name_class = {'project':ProjectAttachment,
            'organization':OrganizationAttachment,
            'investment':InvestmentAttachment,
            }

    def render(self,context,instance,placeholder):
        request = context['request']
        if request.GET.has_key('id'):
            id = request.GET['id']
            name = self.model.name
            if name=='project':
                attachs = ProjectAttachment.objects.filter(project=id)
            elif name=='organization':
                attachs = OrganizationAttachment.objects.filter(organization=id)
            elif name=='investment':
                attachs = InvestmentAttachment.objects.filter(investment=id)
        context.update({'attachments':attachs})
        return context

plugin_pool.register_plugin(CMSSamplingPlugin)
plugin_pool.register_plugin(CMSListImagePlugin)
plugin_pool.register_plugin(CMSSponsorsPlugin)
plugin_pool.register_plugin(CMSGlobalSearchListPlugin)
