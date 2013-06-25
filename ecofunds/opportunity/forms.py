from django import forms
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from ecofunds.models import OpportunityType, Activity
from ecofunds.forms import AdvancedSearchForm

OPPORTUNITYTYPE_CHOICES = (('', 'Choose an opportunity type'),) + tuple(opportunityType.objects.all().values_list('id', 'name'))
ACTIVITY_CHOICES = (('', 'Choose an activity type'),) + tuple(Activity.objects.all().values_list('activity_id', 'name'))

class OpportunityAdvancedSearchForm(AdvancedSearchForm):

    s_opportunity_type = forms.IntegerField(label=_('Opportunity type'), widget=forms.Select(choices=OPPORTUNITYTYPE_CHOICES, attrs={'class':''}))
    
    s_all_type_opportunities = forms.BooleanField(label=_('All opportunity types'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_opportunity_id = forms.IntegerField(widget=forms.HiddenInput())

    s_opportunity = forms.CharField(label=_('Opportunity'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of an opportunity')}))
    s_all_opportunities = forms.BooleanField(label=_('All opportunities'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

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