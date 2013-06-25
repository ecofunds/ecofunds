from django import forms
from django.core.cache import cache
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from ecofunds.models import Activity,Project, Currency
from ecofunds.forms import AdvancedSearchForm
from ajax_select import make_ajax_field

import datetime

from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class MyRadioFieldRenderer(forms.widgets.RadioFieldRenderer):

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        return mark_safe(u'<ul class="radio-buttons">\n%s\n</ul>' % 
                u'\n'.join([u'<li>%s</li>'
                % force_unicode(w) for w in self]))

#PROJECT_TYPES_CHOICES = (
#    ('1','Choose an activity type'),
#    ('2','Aquatic conservation'),
#    ('3','Access and benefit sharing'),
#    ('4','Biocommerce'),
#    ('5','Capacity building&nbsp; Institutional strengthening'),
#    ('6','Climate change (not REDD+)'),
#    ('7','Law/Regulation'),
#    ('8','Financial mechanisms'),
#    ('9','Funding / Supporting Projects'),
#    ('10','Education / Awareness'),
#    ('11','Indigenous people and local communities'),
#    ('12','Landscape conservation'),
#    ('13','Mitigation/Compensation of impacts'),
#    ('14','Networks'),
#    ('15','Payment for environmental services'),
#    ('16','Protected areas'),
#    ('17','REDD/REDD+'),
#    ('18','Research / Monitoring'),
#    ('19','Species management'),
#    ('20','Sustainable development'),
#    ('21','Sustainable production'),
#    ('22','Voluntary standards'),
#    ('23','Waste treatment')
#)

ACTIVITY_CHOICES = (('', 'Choose an activity type'),) + tuple(Activity.objects.all().values_list('activity_id', 'name'))

class ProjectAdvancedSearchForm(AdvancedSearchForm):

    s_project_name = forms.CharField(label=_('Project name'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of a project')}))
    s_all_project_name = forms.BooleanField(label=_('All projects'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))    

    s_project_activity_type = forms.IntegerField(label=_('Project activity type'), widget=forms.Select(choices=ACTIVITY_CHOICES, attrs={'class':''}))

    s_all_project_activity_type = forms.BooleanField(label=_('All activities types'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_type_organization = forms.CharField(label=_('Organization type'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter an organization type')}))
    s_all_type_organizations = forms.BooleanField(label=_('All organization types'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_organization = forms.CharField(label=_('Organization'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of an organization')}))
    s_all_organizations = forms.BooleanField(label=_('All organizations'), widget=forms.CheckboxInput(attrs={'class':'check', 'value': 0}))

    s_country = forms.CharField(label=_('Country'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of a country')}))
    s_state = forms.CharField(label=_('State'), widget=forms.TextInput(attrs={'class':'combo','autocomplete':'off','placeholder': _('Enter the name of a state')}))

    s_investments_from = forms.CharField(label=_('Show investments from:'), widget=forms.TextInput(attrs={'class':'numero'}))
    s_investments_to = forms.CharField(label=_('to'), widget=forms.TextInput(attrs={'class':'numero'}))


    s_date_from = forms.DateTimeField(label=_('Execution period:'), widget=forms.TextInput(attrs={'class':'data'}))
    s_date_to = forms.CharField(label=_('to'), widget=forms.TextInput(attrs={'class':'data'}))


    def _force_data(self):
        if not hasattr(self, 'cleaned_data'):
            self.is_valid()
        if not hasattr(self, 'cleaned_data'):
            self.cleaned_data = {}

    def get_value(self, key, persist=False):
        
        value = None
        #if self.data.has_key(key):
        #    
        #    self._force_data()
        #    if self.cleaned_data.has_key(key):
        #        value = self.cleaned_data[key]

        #    if value:
        #        cache.set(key, value)
        #    else :
        #        value = self.data.get(key)

        #        if not value:
        #            value = cache.get(key)
        #            self.cleaned_data[key] = value
        #        else:
        #            cache.set(key, value)
        #else:
        #    if persist:
        #        value = cache.get(key)
        #        self._force_data()
        #        self.cleaned_data[key] = value
        #    else:
        #        cache.delete(key)

        if hasattr(self, 'cleaned_data') and self.cleaned_data.has_key(key):
            value = self.cleaned_data[key]

        if not value:
            value = self.data.get(key, '')

        if not value:
            value = self.initial.get(key, '')

        return value

class ProjectForm(ModelForm):
    title = forms.CharField(label=_('Project name'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter the name of a project')}))
    acronym = forms.CharField(label=_('Acronym'), required=False, widget=forms.TextInput(attrs={'placeholder': _('Enter the abbreviation of a project')}))
    description = forms.CharField(label=_('Project description'), required=True, widget=forms.Textarea(attrs={'placeholder': _('Enter the description of a project')}))
    
    cat_choices = [('True',_('Project')),('False',_('Program'))]
    category = forms.ChoiceField(choices=cat_choices,widget=forms.RadioSelect(renderer=MyRadioFieldRenderer),initial='True',required=True)

    includes_choices = [('True',_('Yes')),('False',_('No'))]
    include = forms.ChoiceField(choices=includes_choices, widget=forms.RadioSelect(renderer=MyRadioFieldRenderer),
            label=_("Is the project or program included in a program?"),initial='False',required=False)
    
    grant_from = forms.DateField(label=_("Start date"), required=True, widget=forms.DateInput(attrs={'class':'data'}))
    grant_to = forms.DateField(label=_("Expected completion"), required=True, widget=forms.DateInput(attrs={'class':'data'}))

    currency = forms.ModelChoiceField(queryset=Currency.objects.all(),label=_('Estimated budget'), required=True, widget=forms.Select(attrs={'class':'select-curto moeda'}))
    budget = forms.FloatField(widget=forms.TextInput(attrs={'class':'numero'}), required=True)
    
    email = forms.EmailField(label=_('Email'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter the email')}))

    phone_country_prefix_01 = forms.CharField(label=_('Phone number 01'), required=True, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone_local_prefix_01 = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone_number_01 = forms.CharField(label=_('Phone number 01'), required=True, widget=forms.TextInput(attrs={'class':'telefone'}))
    
    phone_country_prefix_02 = forms.CharField(label=_('Phone number 02'), required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone_local_prefix_02 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone_number_02 = forms.CharField(label=_('Phone number 02'), required=False, widget=forms.TextInput(attrs={'class':'telefone'}))
    
    fax_country_prefix = forms.CharField(label=_('FAX'), required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    fax_local_prefix = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    fax = forms.CharField(label=_('FAX'), required=False, widget=forms.TextInput(attrs={'class':'telefone'}))

    website = forms.CharField(label=_('Website'), required=False, widget=forms.TextInput(attrs={'placeholder': _('Enter the website')}))

    #activities = forms.ModelChoiceField(queryset=Activity.objects.all(),required=True)
    activity_description = forms.CharField(label=_('Activity description'), required=False, widget=forms.Textarea(attrs={'placeholder': _('Enter the description of activity')}))

    class Meta:
        model = Project
        exclude = ('entity_id',)
        fields = ('title','description','acronym','image','category','include','organization',
                'main_organization','grant_from','grant_to','currency','budget','email','phone_local_prefix_01','phone_country_prefix_01','phone_number_01',
                'phone_country_prefix_02','phone_country_prefix_02',
                'phone_number_02','fax_country_prefix','fax_local_prefix','fax','website','locations','activities','activity_description')

    main_organization = make_ajax_field(Project,'main_organization','organization', help_text=_('Enter text to search'), label=_('Main executor organization'), required=True)
    organization = make_ajax_field(Project,'organization','organization',help_text=_('Enter text to search'),label=_('Add other executor organizations'), required=False)
    locations = make_ajax_field(Project,'locations','location',help_text=_('Enter text to search'),label=_('Add countries, states and cities where the project is'), required=True)
    activities = make_ajax_field(Project,'activities','activity',help_text=_('Enter text to search'),label=_('Add activity types'), required=True)
    child_projects = make_ajax_field(Project,'sub_projects','project',help_text=('Enter text to search'),label=_('Add a project'),required=False)
    father_projects = make_ajax_field(Project,'sub_projects','project',help_text=('Enter text to search'),label=_('Add a project'),required=False)
