from django import forms
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from ecofunds.models import *
from ecofunds.user.models import UserProfile
from ecofunds.forms import AdvancedSearchForm

from django.forms import ModelForm
from ajax_select import make_ajax_field

from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class MyRadioFieldRenderer(forms.widgets.RadioFieldRenderer):

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        return mark_safe(u'<ul class="radio-buttons">\n%s\n</ul>' % 
                u'\n'.join([u'<li>%s</li>'
                % force_unicode(w) for w in self]))

#INVESTMENTFOCUS_CHOICES = (
#    ('', 'Choose a project activity type'),
#    ('2', 'Aquatic conservation'),
#    ('3', 'Access and benefit sharing'),
#    ('4', 'Biocommerce'),
#    ('5', 'Capacity building&nbsp; Institutional strengthening'),
#    ('6', 'Climate change (not REDD+)'),
#    ('7', 'Law/Regulation'),
#    ('8', 'Financial mechanisms'),
#    ('9', 'Funding / Supporting Projects'),
#    ('10', 'Education / Awareness'),
#    ('11', 'Indigenous people and local communities'),
#    ('12', 'Landscape conservation'),
#    ('13', 'Mitigation/Compensation of impacts'),
#    ('14', 'Networks'),
#    ('15', 'Payment for environmental services'),
#    ('16', 'Protected areas'),
#    ('17', 'REDD/REDD+'),
#    ('18', 'Research / Monitoring'),
#    ('19', 'Species management'),
#    ('20', 'Sustainable development'),
#    ('21', 'Sustainable production'),
#    ('22', 'Voluntary standards'),
#    ('23', 'Waste treatment')
#)

#ORGANIZATIONTYPE_CHOICES = (
#    ('', 'Choose an organization type'),
#    ('2', 'Non-profit organization'),
#    ('3', 'Private company'),
#    ('4', 'Government agency'),
#    ('5', 'Bilateral/Multilateral agency'),
#    ('6', 'Academic/Research institution'),
#    ('7', 'Network'),
#    ('8', 'Other')
#)

ORGANIZATIONTYPE_CHOICES = (('', 'Choose an organization type'),) + tuple(OrganizationType.objects.all().values_list('id', 'name'))
ACTIVITY_CHOICES = (('', 'Choose an activity type'),) + tuple(Activity.objects.all().values_list('activity_id', 'name'))

class OrganizationAdvancedSearchForm(AdvancedSearchForm):

   

    s_organization_type = forms.IntegerField(label=_('Organization type'), widget=forms.Select(choices=ORGANIZATIONTYPE_CHOICES, attrs={'class':''}))
    
    s_all_type_organizations = forms.BooleanField(label=_('All organization types'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_organization_id = forms.IntegerField(widget=forms.HiddenInput())

    s_organization = forms.CharField(label=_('Organization'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of an organization')}))
    s_all_organizations = forms.BooleanField(label=_('All organizations'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_country = forms.CharField(label=_('Country'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of a country')}))
    s_state = forms.CharField(label=_('State'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of a state')}))

    s_investments_focus = forms.IntegerField(label=_('Investments focus'), widget=forms.Select(choices=ACTIVITY_CHOICES, attrs={'class':''}))
    
    s_all_investments_focus = forms.BooleanField(label=_('All project activities focus'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_investment_date_from = forms.CharField(label=_('From'), widget=forms.TextInput(attrs={'class':'data'}))
    s_investment_date_to = forms.CharField(label=_('To'), widget=forms.TextInput(attrs={'class':'data'}))
    s_all_investment_date = forms.BooleanField(label=_('All investments'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))



    s_estimated_investments_value_from = forms.CharField(label=_('Show investments from:'), widget=forms.TextInput(attrs={'class':'numero'}))
    s_estimated_investments_value_to = forms.CharField(label=_('To'), widget=forms.TextInput(attrs={'class':'numero'}))
    s_all_investments_received = forms.BooleanField(label=_('All investments received'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))
    
    def _force_data(self):
        if not hasattr(self, 'cleaned_data'):
            self.is_valid()
        if not hasattr(self, 'cleaned_data'):
            self.cleaned_data = {}

    def get_value(self, key, persist=False):
        
        value = None
        if self.data.has_key(key):
            
            self._force_data()
            if self.cleaned_data.has_key(key):
                value = self.cleaned_data[key]

            if value:
                cache.set(key, value)
            else :
                value = self.data.get(key)

                if not value:
                    value = cache.get(key)
                    self.cleaned_data[key] = value
                else:
                    cache.set(key, value)
        else:
            if persist:
                value = cache.get(key)
                self._force_data()
                self.cleaned_data[key] = value
            else:
                cache.delete(key)

        return value


class OrganizationForm(ModelForm):
    name = forms.CharField(label=_('Organization name'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter the name of a organization')}))
    acronym = forms.CharField(label=_('Acronym'), required=False, widget=forms.TextInput(attrs={'placeholder': _('Enter the abbreviation of a organization')}))
    mission = forms.CharField(label=_('Organization description'), required=True, widget=forms.Textarea(attrs={'placeholder': _('Enter the description of a organization')}))

    type = forms.ModelChoiceField(queryset=OrganizationType.objects.all(),label=_('Organization type'), required=True)
    ceo = forms.CharField(label=_('CEO/President/Director'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter the CEO/President\'s name')}))
    toolkit = forms.CharField(label=_('Toolkit profile web address'),required=False, widget=forms.TextInput(attrs={'placeholder': _('Enter the web address of your toolkit profile')}))
    
    admin_choices = [('True',_('Yes')),('False',_('No'))]
    admin = forms.ChoiceField(choices=admin_choices, widget=forms.RadioSelect(renderer=MyRadioFieldRenderer),
            label=_("Will you be an administrador of this organization in Ecofunds?"))
    
    street1 = forms.CharField(label=_('Address'),required=True, widget=forms.TextInput(attrs={'class':'endereco','placeholder': _('Enter the address of your organization')}))
    street2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'endereco'}))
    zip = forms.CharField(label=_('ZIP'),required=False, widget=forms.TextInput(attrs={'class':'texto-curto','placeholder': _('Enter the ZIP code of your organization')}))

    city = forms.CharField(label=_('City'), required=True, widget=forms.TextInput(attrs={'class':'texto-curto'}))
    
    email = forms.EmailField(label=_('Email'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter the email')}))
    
    phone_country_prefix = forms.CharField(label=_('Phone number 01'), required=True, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone_local_prefix = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'telefone',  'maxlength':'8'}))

    fax_country_prefix = forms.CharField(label=_('FAX'), required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    fax_local_prefix = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    fax_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'telefone',  'maxlength':'8'}))
    
    website = forms.URLField(label=_('Website'), required=False, widget=forms.TextInput(attrs={'placeholder': _('Enter the website')}))
    
    class Meta:
        model = Organization
        fields = ('name','acronym','mission','image','type','toolkit','admin','street1',
        'street2','zip','country','city','email','phone_country_prefix','phone_local_prefix',
        'phone_number','fax_country_prefix','fax_local_prefix','fax_number','url','website','state')

    country = make_ajax_field(Organization,'country','country',help_text=_('Search a country name'),
            label=_('Country'),required=True)
    connections = make_ajax_field(Organization,'userprofiles','userprofile',
            help_text=_('Search for a registered user'),label=_('Add administrators to this organization'),required=False)
    projects = make_ajax_field(Organization,'projects','project',
            help_text=_('Search for a registered project'),label=_('Add projects executed by this organization'),required=False)
    
    state = make_ajax_field(Organization,'state','location',help_text=_('Enter text to search'),label=_('Search for a state, region or province'), required=True)
