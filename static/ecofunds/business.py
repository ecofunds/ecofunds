from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache

from ecofunds.models import *
from ecofunds.project.forms import *
from ecofunds.organization.forms import *
from ecofunds.investment.forms import *

import datetime

from django import db
from django.db.models import Q
from ecofunds.templatetags.tags import currency
import locale
import re
from babel import numbers
from django.utils.translation import ugettext_lazy as _

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Max

def format_currency(value):
    return numbers.format_currency(
            float(value),
            numbers.get_currency_symbol('USD', 'en_US'),
            u'\xa4\xa4 #,##0.00', locale='pt_BR')





def trans_date(v):
    v = str(v)
    print 'Data ', v
    if len(v)==10:

        if re.search('/', v):
            tup = v.split('/')
            tup[0], tup[2] = tup[2], tup[0]
        else:
            tup = v.split('-')
        if int(tup[0]) <= 1800:
            return ''
        v = tup[0] + '-'+tup[1] + '-' + tup[2]
        return v
    else:
        return ''


def print_queries(list):
    if settings.DEBUG:
           db.reset_queries
           for x in list:
               break
           file = open("c:/queries.sql", "w")
           for item in db.connection.queries:
               sql = item['sql']
               file.write('****** '+sql.replace('FROM', '\n\tFROM').replace('WHERE', '\n\tWHERE'))
               file.write('\n')
           file.close



class InvestmentData(object):
    @staticmethod
    def item(id):
        #print('id: '+str(id))
        if id:
            return Investment.objects.get(pk=id)
        else:
            return None

    @staticmethod
    def list(order_by=None, **kwargs):
        """
        List all investments
        """
        query = Investment.objects

        if kwargs != None and kwargs.keys().count > 0:
            query = query.filter(active=1,**kwargs)

        if order_by:
            query = query.order_by(order_by)
        else:
            query = query.order_by('-created_at')

        return query

    @staticmethod
    def paginatedAttachmentList(investment_id, quantity, page, order_by=None, **kwargs):
        if quantity is None or not isinstance(quantity, (int, long)) or quantity == 0:
            quantity = 10

        query = Attachment.objects.filter(investments__investment__id__exact=investment_id)
        
        paginator = Paginator(query, quantity)
        #print(paginator.object_list)
        try:
            list = paginator.page(page)
        except PageNotAnInteger:
            list = paginator.page(1)
        except EmptyPage:
            list = paginator.page(paginator.num_pages)

        return list

    @staticmethod
    def paginatedList(quantity, page, order_by=None, project_id=None, **kwargs):

        if quantity is None or not isinstance(quantity, (int, long)) or quantity == 0:
            quantity = 10
        list = InvestmentData.list(order_by, **kwargs)
        if not project_id is None:
            list.filter((Q(recipient_entity_id=project_id)|Q(funding_entity_id=project_id)))
        
        
        #print_queries(list)
        orig_list = list
        paginator = Paginator(list, quantity)
        
        try:
            list = paginator.page(page)
        except PageNotAnInteger:
            list = paginator.page(1)
        except EmptyPage:
            list = paginator.page(paginator.num_pages)

        return list, orig_list

    @staticmethod
    def listByQuery(query):
        return Investment.objects.filter(query)

    @staticmethod
    def suggestList(search, quantity):
        pass

    @staticmethod
    def filteredList(request, quantity):
        if request.method == "POST":
            data = request.POST
            form = InvestmentAdvancedSearchForm(request.POST, initial={'limit': quantity, 'page':data.get('page')})
            request.session['investment_data_filters'] = data
        else:
            if len(request.GET.items()) == 0 and request.session.has_key('investment_data_filters'):
                s_project_name = request.GET.get('s_project_name')
                s_organization = request.GET.get('s_organization')
                if s_project_name or s_organization:
                    data = request.GET
                else:
                    data = request.session['investment_data_filters']
                form = InvestmentAdvancedSearchForm(data, initial={'limit': quantity, 'page':data.get('page')})
            else:
                data = request.GET
                form = InvestmentAdvancedSearchForm(data)

        labels = {}
        filters = {}
        page = data.get('page')
        order_by = data.get('order_by')
        search = data.get('search')


        project_id = None
        if request.GET.has_key('project'):
            project_id = request.GET['project'] 

        s_investment_type = data.get('s_investment_type')

        s_investment_from = data.get('s_investment_date_from')
        s_investment_to = data.get('s_investment_date_to')

        s_investment_from = trans_date(s_investment_from)
        s_investment_to = trans_date(s_investment_to)


        s_investment_amount_min = data.get('s_investment_from')
        s_investment_amount_max = data.get('s_investment_to')

        if s_investment_from and s_investment_to:
            if s_investment_from > s_investment_to:
                s_investment_from, s_investment_to = s_investment_to, s_investment_from



        if s_investment_amount_max and s_investment_amount_min:
            if float(s_investment_amount_min) > 0 and float(s_investment_amount_max) > 0:
                if float(s_investment_amount_max) < float(s_investment_amount_min):
                    s_investment_amount_max, s_investment_amount_min = s_investment_amount_min, s_investment_amount_max


        s_organization_id = data.get('s_organization_id')
        s_organization_type = data.get('s_organization_type')
        s_organization_name = data.get('s_organization')

        s_project_name = data.get('s_project_name')

        s_investment_country = data.get('s_country')
        s_investment_state = data.get('s_state')

        if  (s_investment_type != None and s_investment_type != ''):
            filters.update({'type__id': int(s_investment_type)})
            labels.update({'s_investment_type': InvestmentType.objects.get(pk=int(s_investment_type)).name})

        #date

        start_date = trans_date(s_investment_from)

        if  (start_date):
            filters.update({'created_at__gte': start_date})
            labels.update({'s_investment_date_from': _("Investment date") + " >= " + start_date})

        end_date = trans_date(s_investment_to)
        if  (end_date):
            filters.update({'created_at__lte': end_date})
            labels.update({'s_investment_date_to': _("Investment date") + " <= " + end_date})

        #amount
        if  (not s_investment_amount_min is None) and s_investment_amount_min != '' and float(s_investment_amount_min) > 0:
            filters.update({'amount_usd__gte': s_investment_amount_min})
            labels.update({'s_investment_from': _("Investment value") + " >= " + format_currency( s_investment_amount_min )})

        if  (not s_investment_amount_max is None) and s_investment_amount_max != ''  and float(s_investment_amount_max) > 0:
            filters.update({'amount_usd__lte': s_investment_amount_max})
            labels.update({'s_investment_to':  _("Investment value") + " <= " + format_currency( s_investment_amount_max)})


        if  s_organization_type != None and s_organization_type != '':
            filters.update({'recipient_organization__type__id': int(s_organization_type)})
            labels.update({'s_organization_type': OrganizationType.objects.get(pk=int(s_organization_type)).name})

        if  s_organization_id != None and s_organization_id != '':
            filters.update({'recipient_organization__id__exact': s_organization_id})
            labels.update({'s_organization_id': Organization.objects.get(pk=int(s_organization_id)).name})

        if  s_organization_name != None and s_organization_name != '':
            filters.update({'recipient_organization__name__icontains': s_organization_name})
            labels.update({'s_organization': s_organization_name})
        elif search != None and search != '':
            filters.update({'recipient_organization__name__icontains': search})


        if (not s_project_name is None) and s_project_name != '':
            filters.update({'recipient_entity__title__icontains': s_project_name})
            labels.update({'s_project_name': s_project_name})

        if  s_investment_country != None and s_investment_country != '':
            filters.update({'recipient_organization__country__name': s_investment_country})
            labels.update({'s_country': s_investment_country})

        if  s_investment_state != None and s_investment_state != '':
            filters.update({'recipient_organization__state__icontains': s_investment_state})
            labels.update({'s_state': s_investment_state})

        
        list, orig_list = InvestmentData.paginatedList(quantity, page, order_by, project_id, **filters)
        print orig_list.query
        return list, form, labels, orig_list
    
class OrganizationData(object):

    @staticmethod
    def item(id):
        return Organization.objects.get(pk=id)

    @staticmethod
    def list(order_by=None, **kwargs):
        """
        List all organizations
        """
        query = Organization.objects
        name = None
        if kwargs != None:
            # cambalhota pra filtrar por nome OU acronimo
            if kwargs.has_key('name__icontains') and kwargs['name__icontains']:
                name = kwargs['name__icontains']
                del(kwargs['name__icontains'])
            query = query.filter(active=1,**kwargs)

        if name:
            query = query.filter(Q(name__icontains=name)|Q(acronym=name))

        if order_by :
            if order_by == 'count_projects' or order_by == '-count_projects':
                query = query.annotate(count_projects = Count('projects'))
            elif order_by == '-investment_amnt':
                query = query.annotate(investment_amnt = Sum('funding_investments__amount'))
            elif order_by == '-last_investment_date':
                query = query.annotate(last_investment_date = Max('funding_investments__created_at'))

            query = query.order_by(order_by)
        else :
            query = query.order_by('-created_at')

        return query

    @staticmethod
    def paginatedList(quantity, page, order_by=None, **kwargs):

        if quantity is None or not isinstance(quantity, (int, long)):
            quantity = 10

        paginator = Paginator(OrganizationData.list(order_by, **kwargs), quantity)
        
        

        try:
            list = paginator.page(page)
        except PageNotAnInteger:
            list = paginator.page(1)
        except EmptyPage:
            list = paginator.page(paginator.num_pages)

        return list

    @staticmethod
    def get_filters_labels_from_request_data(data, prefix_property=''):

        labels = {}
        filters = {}

        search = None

        s_organization_type = data.get('s_organization_type')
        s_all_type_organizations = data.get('s_all_type_organizations')
        s_organization = data.get('s_organization')
        s_all_organizations = data.get('s_all_organizations')

        s_country = data.get('s_country')
        s_state = data.get('s_state')

        s_investments_focus = data.get('s_investments_focus')
        s_all_investments_focus = data.get('s_all_investments_focus')

        s_investment_date_from = data.get('s_investment_date_from')
        s_investment_date_to = data.get('s_investment_date_to')
        s_all_investment_date = data.get('s_all_investment_date')

        s_investment_date_from = trans_date(s_investment_date_from)
        s_investment_date_to = trans_date(s_investment_date_to)


        s_estimated_investments_value_from = data.get('s_estimated_investments_value_from')
        s_estimated_investments_value_to = data.get('s_estimated_investments_value_to')
        s_all_investments_received = data.get('s_all_investments_received')

        if data.has_key('search'):
            search = data.get('search')

        if  s_organization_type != None and s_organization_type != '' :
            filters.update({prefix_property+'type_id__exact': s_organization_type})
            labels.update({'s_organization_type': OrganizationType.objects.get(pk=int(s_organization_type)).name})

        if  s_organization != None and s_organization != '':
            filters.update({prefix_property+'name__icontains': s_organization})
            labels.update({'s_organization': s_organization})

        if  s_country != None and s_country != '':
            filters.update({prefix_property+'country__name__icontains': s_country})
            labels.update({'s_country': s_country})

        if  s_state != None and s_state != '':
            filters.update({prefix_property+'state__icontains': s_state})
            labels.update({'s_state': s_state})

        if not s_all_investments_focus:
            if  s_investments_focus != None and s_investments_focus != '':
                filters.update({prefix_property+'projects_organizations__entity__projects_activities__activity_id__exact': s_investments_focus})
                labels.update({'s_investments_focus': Activity.objects.get(pk=int(s_investments_focus)).name})

        investments = Investment.objects
        inv_date = False

        if not s_all_investment_date:
            if  s_investment_date_from != None and s_investment_date_from != '':
                investments = investments.filter(created_at__gte=s_investment_date_from)
                start_date = s_investment_date_from.split('-')
                start_date =  date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                labels.update({'s_investment_date_from': _("Last investment") + " >= " +start_date.strftime("%d/%m/%Y")})
                inv_date = True

            if  s_investment_date_to != None and s_investment_date_to != '':
                investments = investments.filter(created_at__lte=s_investment_date_to)
                end_date = s_investment_date_to.split('-')
                end_date =  date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
                labels.update({'s_investment_date_to': _("Last investment") + " <= " +end_date.strftime("%d/%m/%Y")})
                inv_date = True

        inv_value = False

        if not s_all_investments_received:
            if s_estimated_investments_value_from != 0 and s_estimated_investments_value_to != 0:
                if  s_estimated_investments_value_from != None and s_estimated_investments_value_from != '':
                    investments = investments.filter(amount_usd__gte=s_estimated_investments_value_from)
                    labels.update({'s_estimated_investments_value_from': s_estimated_investments_value_from})
                    inv_value = True

                if  s_estimated_investments_value_to != None and s_estimated_investments_value_to != '':
                    investments = investments.filter(amount_usd__lte=s_estimated_investments_value_to)
                    labels.update({'s_estimated_investments_value_to': s_estimated_investments_value_to})
                    inv_value = True

        if inv_date or inv_value:
            ids = investments.values('recipient_organization_id')
            if len(ids) > 0:
                filters.update({prefix_property+'id__in': ids})

        return filters, labels

    @staticmethod
    def filteredList(request, quantity, **filters):

        if request.method == "POST":
            data = request.POST
            form = OrganizationAdvancedSearchForm(request.POST, initial={'limit': quantity, 'page':data.get('page')})
            request.session['organization_data_filters'] = data
        else:
            if request.session.has_key('organization_data_filters'):
                data = request.session['organization_data_filters']
                form = OrganizationAdvancedSearchForm(data, initial={'limit': quantity, 'page':data.get('page')})
            else:
                data = request.GET
                form = OrganizationAdvancedSearchForm(data)

        



        f, labels = OrganizationData.get_filters_labels_from_request_data(data)

        
       

        criteria = {}

        if filters.keys().count > 0:
            criteria.update(filters)

        criteria.update(f)
        
        page = data.get('page')
        order_by = data.get('order_by')

        if quantity == 0:
            return OrganizationData.list(order_by, **criteria)
        
        return OrganizationData.paginatedList(quantity, page, order_by, **criteria), form, labels

    @staticmethod
    def suggestList(search, quantity):
        
        return OrganizationData.paginatedList(quantity, 1, 'name', title__icontains = search)

class ProjectData(object):

    @staticmethod
    def item(id):
        try:
            return Project.objects.get(pk=id)
        except Project.DoesNotExist:
            return 

    @staticmethod
    def locationList(**kwargs):
        query = ProjectLocation.objects
        if kwargs != None and kwargs.keys().count > 0:
            query = query.filter(**kwargs)
        return query

    @staticmethod
    def locationFilteredList(request):
        filters = {}

        if request.method == "POST":
            data = request.POST
        else:
            data = request.GET

        query = ProjectLocation.objects.filter(entity__validated=1)
        
        filters, labels = ProjectData.get_filters_labels_from_request_data(data, 'entity__')

        if filters != None and filters.keys().count > 0:
            query = query.filter(**filters)

        return query

    @staticmethod
    def attachmentList(project_id, **kwargs):
        """
        List all attachments
        """
        query = ProjectAttachment.objects.filter(entity_id=project_id)

        if kwargs != None and kwargs.keys().count > 0:
            query = query.filter(**kwargs)

        query = query.order_by('-created_at')

        return query

    @staticmethod
    def paginatedAttachmentList(project_id, quantity, page, **kwargs):

        paginator = Paginator(ProjectData.attachmentList(project_id, **kwargs), quantity)
        

        if page is None:
            page = 1
        
        try:
            list = paginator.page(page)
        except PageNotAnInteger:
            list = paginator.page(1)
        except EmptyPage:
            list = paginator.page(paginator.num_pages)

        return list

    @staticmethod
    def list(order_by=None, **kwargs):
        """
        List all projects
        """
        query = Project.objects

        if kwargs != None and kwargs.keys().count > 0:
            query = query.filter(active=1,**kwargs)

        if order_by:
            query = query.order_by(order_by)
        else:
            query = query.order_by('-created_at')

        return query
    
    @staticmethod
    def paginatedList(quantity, page, order_by=None, **kwargs):
        list = ProjectData.list(order_by, **kwargs)
        paginator = Paginator(list, quantity)
        if page is None:
            page = 1
        try:
            list = paginator.page(page)
        except PageNotAnInteger:
            list = paginator.page(1)
        except EmptyPage:
            list = paginator.page(paginator.num_pages)

        return list

    @staticmethod
    def get_filters_labels_from_request_data(data, prefix_property=''):

        labels = {}
        filters = {}

        search = None

        s_project_name = data.get('s_project_name')
        s_all_project_name = data.get('s_all_project_name')

        s_project_activity_type = data.get('s_project_activity_type')
        s_all_project_activity_type = data.get('s_all_project_activity_type')

        s_type_organization = data.get('s_type_organization')
        s_all_type_organizations = data.get('s_all_type_organizations')

        s_organization = data.get('s_organization')
        s_organization_id = data.get('s_organization_id')
        s_all_organizations = data.get('s_all_organizations')

        s_country = data.get('s_country')
        s_state = data.get('s_state')

        s_investments_from = data.get('s_investments_from')
        s_investments_to = data.get('s_investments_to')


        s_grant_from = trans_date(data.get('s_date_from'))
        s_grant_to = trans_date(data.get('s_date_to'))
        


        if data.has_key('search'):
            search = data.get('search')

        if not s_all_project_name:
            if  (s_project_name != None and s_project_name != '') :
                filters.update({prefix_property+'title__icontains': s_project_name})
                labels.update({'s_project_name': s_project_name})

            elif search != None and search != '':
                filters.update({prefix_property+'title__icontains': search})

        if  s_project_activity_type != None and s_project_activity_type != '' :
            filters.update({prefix_property+'projects_activities__activity_id__exact': s_project_activity_type})
            labels.update({'s_project_activity_type': Activity.objects.get(pk=int(s_project_activity_type)).name})

        if not s_all_type_organizations:
            if  s_type_organization != None and s_type_organization != '' :
                filters.update({prefix_property+'organizations__organization__type_id__exact': s_type_organization})
                labels.update({'s_type_organization': OrganizationType.objects.get(pk=int(s_type_organization)).name})

        if  s_organization_id != None and s_organization_id != '':
            filters.update({prefix_property+'organizations__organization__id__exact': s_organization_id})
            labels.update({'s_organization': Organization.objects.get(pk=int(s_organization_id)).name})

        if not s_all_organizations:
            if  s_organization != None and s_organization != '':
                filters.update({prefix_property+'organizations__organization__name__icontains': s_organization})
                labels.update({'s_organization': s_organization})

        if  s_country != None and s_country != '':
            filters.update({prefix_property+'projects_locations__location__country__name__icontains': s_country})
            labels.update({'s_country': s_country})

        if  s_state != None and s_state != '':
            filters.update({prefix_property+'projects_locations__location__name__icontains': s_state})
            labels.update({'s_state': s_state})
            


        if s_investments_from!= None and (s_investments_from!= ''):
            filters.update({prefix_property+'budget__gte': s_investments_from})
            if s_investments_from != '0.00':
                labels.update({prefix_property+'s_investments_from': _('budget') + ' >= ' + format_currency( s_investments_from)})
        if s_investments_to!=None and (s_investments_to!= ''):
            filters.update({prefix_property+'budget__lte': s_investments_to})
            if s_investments_to != '0.00':
                labels.update({prefix_property+'s_investments_to': _('budget') +' <= ' + format_currency( s_investments_to)})

                
        print 'Grant from: ', s_grant_from
        if s_grant_from:
            filters.update({prefix_property+'grant_from__gte': s_grant_from})
        if s_grant_to:
            filters.update({prefix_property+'grant_to__lte': s_grant_to})

        
        return filters, labels

    @staticmethod
    def filteredList(request, quantity):

        if request.method == "POST":
            data = request.POST
            form = ProjectAdvancedSearchForm(data, initial={'limit': quantity, 'page':data.get('page')})
            request.session['project_data_filters'] = data
        else:
            if len(request.GET.items()) == 0 and request.session.get('project_data_filters'):
                data = request.session['project_data_filters']
                form = ProjectAdvancedSearchForm(data, initial={'limit': quantity, 'page':data.get('page')})
            else:
                data = request.GET
                form = ProjectAdvancedSearchForm(data)
        
        page = data.get('page')
        order_by = data.get('order_by')
        
        filters, labels = ProjectData.get_filters_labels_from_request_data(data)
       

        

        if quantity == 0:
            return ProjectData.list(order_by, **filters)

        return ProjectData.paginatedList(quantity, page, order_by, **filters), form, labels

    @staticmethod
    def suggestList(search, quantity):
        
        return ProjectData.paginatedList(quantity, 1, 'title', title__icontains = search)


class GlobalSearchForm(forms.Form):

    page = forms.IntegerField(widget=forms.HiddenInput())
    order_by = forms.CharField(widget=forms.HiddenInput())
    query = forms.CharField(widget=forms.HiddenInput())
    search_type = forms.CharField(widget=forms.HiddenInput())
