from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.core.cache import cache
from django.db.models import Count
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.db import IntegrityError

from ecofunds.models import *
from ecofunds.user.models import *
from ecofunds.user.notification import notificate
from ecofunds.business import *
from ecofunds.investment.models import InvestmentsPlugin,InvestmentFormPlugin
from ecofunds.investment.forms import InvestmentForm
from ecofunds.views import item_permission_list
from ecofunds.cms_plugins import GenericCMSFormPlugin

from ecofunds.user.permissions import edit_allowance
from django import db

from ecofunds.middleware.forcedresponse import ForceResponse



class CMSInvestmentsPlugin(CMSPluginBase):
    model = InvestmentsPlugin
    name = _("Investment List")
    render_template = "investment/list.html"
    module = _("Investment")

    def render(self, context, instance, placeholder):
        request = context['request']
        list, form, labels, orig_list = InvestmentData.filteredList(request, instance.limit)
        itempermlist = item_permission_list(request,list)
        context.update({
            'itempermlist':itempermlist,
            'list':list,
            'labels':labels,
            'search_investment_form':form,
            'page_detail':instance.page_detail,

            'latest_investments': InvestmentData.list()[:5],
            'count_projects': Project.objects.count,
            'count_organizations': Organization.objects.count,
            'count_organization_types': OrganizationType.objects.count,
            'count_investments': Investment.objects.count,
            'count_investment_types': InvestmentType.objects.count,
            'count_recipient_entity_investments': Investment.objects.values('recipient_entity').annotate(total=Count('recipient_entity')).count,

            'instance':instance,
            'placeholder':placeholder
        })

        context.update(orig_list.aggregate(Sum('amount_usd')))

        if len(list.object_list) == 0:

            cur = db.connection.cursor()
            sql = """
select e.entity_id, e.title, e.resume
from ecofunds_entities e
join ecofunds_investments i on i.recipient_entity_id = e.entity_id
group by e.entity_id, e.title, e.resume
order by i.created_at desc
limit 5
"""
            cur.execute(sql)
            items = cur.fetchall()
            latest = []
            for x in items:
                item = Project()
                item.entity_id = x[0]
                item.title = x[1]
                item.resume = x[2]
                latest.append(item)            
                        
            context.update({'new_project_investments': latest})

        return context

class CMSDetailInvestmentPlugin(CMSPluginBase):
    name = _("Investment Detail")
    render_template = "investment/detail.html"
    module = _("Investment")

    def render(self, context, instance, placeholder):
        request = context['request']
        id = request.GET.get('id')
        page = request.GET.get('page')
        investment = InvestmentData.item(id)
        perm = False
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except UserProfile.DoesNotExist:
                profile = None
            if profile:
                perm = edit_allowance(investment,profile)
        context.update({
            'investment':InvestmentData.item(id),
            'attachments':InvestmentData.paginatedAttachmentList(id, 5, page),
            'highest_investments': InvestmentData.list().order_by('-amount_usd').exclude(pk=id)[:3],
            'similar_investment_types': InvestmentData.list(type_id__exact=investment.type_id).exclude(pk=id)[:3],
            'instance':instance,
            'placeholder':placeholder,
            'perm':perm,
        })
        return context


class CMSFormInvestmentPlugin(GenericCMSFormPlugin):
    model = InvestmentFormPlugin
    name = _("Investment Form")
    render_template = "investment/form.html"
    module = _("Investment")
    DjangoModel = Investment
    DjangoForm = InvestmentForm
    redirect_language = {'pt-br':'../ficha-investimento',
            'en':'../investment-detail',
            'es':'../investment-detail',
            }

    def render(self,context,instance,placeholder):
        request = context['request']
        if request.method=='POST':
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    proj = self.DjangoModel.objects.get(pk=pk_id)
                    projform = self.DjangoForm(request.POST,instance=proj)
                    note_type = 'update'
                except self.DjangoModel.DoesNotExist:
                    projform = self.DjangoForm(request.POST)
                    projform.creater = request.user
            else:
                projform = self.DjangoForm(request.POST)
                note_type='create'
            if projform.is_valid():
                p=projform.save()
                if projform.cleaned_data.get('investment_flow'):
                    for inv in projform.cleaned_data.get('investment_flow'):
                        obj = Investment.objects.get(pk=inv)
                        invflow = InvestmentFlow(father=obj,child=p)
                    try:
                        invflow.save()
                    except IntegrityError:
                        pass
                notificate(p,note_type,request.user,msg=_("test"))
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
                context.update({'formset':self.DjangoForm(instance=proj)})
                return context
            else:
                context.update({'formset':self.DjangoForm() })
                return context

plugin_pool.register_plugin(CMSInvestmentsPlugin)
plugin_pool.register_plugin(CMSDetailInvestmentPlugin)
plugin_pool.register_plugin(CMSFormInvestmentPlugin)
