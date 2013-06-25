from django import forms
from django.core.cache import cache
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from ecofunds.models import *
from ecofunds.forms import AdvancedSearchForm
from ajax_select import make_ajax_field

from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class MyRadioFieldRenderer(forms.widgets.RadioFieldRenderer):

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        return mark_safe(u'<ul class="radio-buttons">\n%s\n</ul>' % 
                u'\n'.join([u'<li>%s</li>'
                % force_unicode(w) for w in self]))

#INVESTMENTTYPE_CHOICES = (
#    ('', 'Choose an investment type'),
#    ('1', 'Donation'),
#    ('1', 'In Kind'),
#    ('1', 'Legal obligations'),
#    ('1', 'Loan'),
#    ('1', 'Matching'),
#    ('1', 'Microcredit'),
#    ('1', 'Voluntary compensations / Mitigations')
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

INVESTMENTTYPE_CHOICES = (('', 'Choose an investment type'),) + tuple(InvestmentType.objects.all().values_list('id', 'name'))
ORGANIZATIONTYPE_CHOICES = (('', 'Choose an organization type'),) + tuple(OrganizationType.objects.all().values_list('id', 'name'))

class InvestmentAdvancedSearchForm(AdvancedSearchForm):
    
    s_investment_type = forms.IntegerField(label=_('Investment type'), widget=forms.Select(choices=INVESTMENTTYPE_CHOICES, attrs={'class':''}))

    s_all_type_investments = forms.BooleanField(label=_('All organization types'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_investment_date_from = forms.CharField(label=_('Show investments from:'), widget=forms.TextInput(attrs={'class':'data'}))
    s_investment_date_to = forms.CharField(label=_('To'), widget=forms.TextInput(attrs={'class':'data'}))
    s_all_investments_date = forms.BooleanField(label=_('All investments received'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_investment_from = forms.CharField(label=_('Show investments from:'), widget=forms.TextInput(attrs={'class':'numero'}))
    s_investment_to = forms.CharField(label=_('To'), widget=forms.TextInput(attrs={'class':'numero'}))
    s_all_investments_value = forms.BooleanField(label=_('All investments value'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_organization_type = forms.IntegerField(label=_('Organization type'), widget=forms.Select(choices=ORGANIZATIONTYPE_CHOICES, attrs={'class':''}))
    
    s_all_type_organizations = forms.BooleanField(label=_('All organization types'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_organization_id = forms.IntegerField(widget=forms.HiddenInput())
    s_organization = forms.CharField(label=_('Organization'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of an organization')}))
    s_all_organizations = forms.BooleanField(label=_('All organizations'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))


    s_project_name = forms.CharField(label=_('Project name'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of a project')}))
    s_all_project_name = forms.BooleanField(label=_('All projects'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_country = forms.CharField(label=_('Country'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of a country')}))
    s_state = forms.CharField(label=_('State'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of a state')}))

    def _force_data(self):
        if not hasattr(self, 'cleaned_data'):
            self.is_valid()
        if not hasattr(self, 'cleaned_data'):
            self.cleaned_data = {}

    def get_value(self, key, persist=False):
        
        value = None
        if hasattr(self, 'cleaned_data') and self.cleaned_data.has_key(key):
            value = self.cleaned_data[key]

        if not value:
            value = self.data.get(key, '')

        if not value:
            value = self.initial.get(key, '')

        return value

class InvestmentForm(ModelForm):
    y_n_choices = [('True',_('Yes')),('False',_('No'))]
    investor_project = forms.ChoiceField(choices=y_n_choices,widget=forms.RadioSelect(renderer=MyRadioFieldRenderer),
            label=_("Is the investment an action of an investor project?"),initial='False',required=False)

    r_project = forms.ChoiceField(choices=y_n_choices,widget=forms.RadioSelect(renderer=MyRadioFieldRenderer),
            label = _("Is the investment direct to a recepient project?"),initial='False',required=False)

    type = forms.ModelChoiceField(queryset=InvestmentType.objects.all(),label=_('Investment type'), widget=forms.Select(attrs={'class':'select-curto'}),required=True)
    date = forms.DateField(label=_('Investment date'), required=True, widget=forms.TextInput(attrs={'class':'data'}))
    estimated_completion = forms.DateField(label=_('Estimated completion date'), required=True, widget=forms.TextInput(attrs={'class':'data'}))

    currency = forms.ModelChoiceField(queryset=Currency.objects.all(),label=_('Investment total value'), required=True, widget=forms.Select(attrs={'class':'select-curto moeda'}))
    amount = forms.FloatField(widget=forms.TextInput(attrs={'class':'numero'}),required=True)
    
    third_party = forms.ChoiceField(choices=y_n_choices,widget=forms.RadioSelect(),label=_('Did the main investor receive this amount from third-party institutions?'),required=False)

    class Meta:
        model = Investment
        fields = ('funding_organization','investor_project','recipient_organization',
                'recipient_entity','funding_entity','r_project','type','date',
                'estimated_completion','currency','amount')

    funding_organization = make_ajax_field(Investment,'funding_organization','organization',help_text=_('Enter text to search'),label=_('Investor organization'), required=True)
    
    recipient_organization = make_ajax_field(Investment,'recipient_organization','organization',help_text=_('Enter text to search'),label=_('Recepient organization'), required=True)
    recipient_entity = make_ajax_field(Investment,'recipient_entity','project',help_text=_('Enter text to search'),label=_('Recipient Project'),
            required = False)
    funding_entity = make_ajax_field(Investment,'funding_entity','project',help_text=_('Enter text to search'),label=_('Investor Project'),
            required = False)

    investment_flow = make_ajax_field(Investment,'investment_flow','investment',help_text=_('Did the main investor received this amount from third-party institutions?'),required=False)
