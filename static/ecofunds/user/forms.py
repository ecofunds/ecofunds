from django import forms
from ecofunds.models import *
from ecofunds.user.models import *
from django.forms import ModelForm
from ajax_select import make_ajax_field
from django.utils.translation import ugettext_lazy as _

from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class MyRadioFieldRenderer(forms.widgets.RadioFieldRenderer):

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        return mark_safe(u'<ul class="radio-buttons">\n%s\n</ul>' % 
                u'\n'.join([u'<li>%s</li>'
                % force_unicode(w) for w in self]))

class UserForm(ModelForm):
    first_name = forms.CharField(label=_('First name'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter the first name of a user')}))
    last_name = forms.CharField(label=_('Last Name'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter the last name of a user')}))
    
    password = forms.CharField(label=_('Password'), required=True, widget=forms.PasswordInput(attrs={'class': 'texto-curto'}))
    check_password = forms.CharField(label=_('Repeat Password'), required=True, widget=forms.PasswordInput(attrs={'class': 'texto-curto'}))
    
    email = forms.EmailField(label=_('Email'), required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter the email')}))
    
    includes_choices = [('True',_('Yes')),('False',_('No'))]
    receive_notes = forms.ChoiceField(choices=includes_choices,widget=forms.RadioSelect(renderer=MyRadioFieldRenderer),
            label=_('Do you want to receive notifications in your email?'),initial='False')
    
    phone_country_prefix_01 = forms.CharField(label=_('Phone number 01'), required=True, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone_local_prefix_01 = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone1 = forms.CharField(label=_('Phone number 01'),required=True, widget=forms.TextInput(attrs={'class':'telefone'}))
    
    phone_country_prefix_02 = forms.CharField(label=_('Phone number 02'), required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone_local_prefix_02 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    phone2 = forms.CharField(label=_('Phone number 02'),required=False, widget=forms.TextInput(attrs={'class':'telefone'}))
    
    fax_country_prefix = forms.CharField(label=_('FAX'), required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    fax_local_prefix = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'prefixo',  'maxlength':'2'}))
    fax = forms.CharField(label=_('FAX'),required=False, widget=forms.TextInput(attrs={'class':'telefone'}))
    
    email_alt = forms.EmailField(label=_('Alternative email'), required=False, widget=forms.TextInput(attrs={'placeholder': _('Enter the alternative email')}))
    title = forms.CharField(label=_('Job Title'),required=False)
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all(),required=False)
    def clean(self):
        cleaned_data = super(self.__class__,self).clean()
        password = cleaned_data.get('password')
        check_password = cleaned_data.get('password')
        if not(password and check_password) and password!=check_password:
            raise forms.ValidationError(_("Passwords don't match "))
        return cleaned_data
    
    class Meta:
        model = UserProfile
        fields = ('first_name','last_name','password',
                'check_password','image','email','title','receive_notes','phone_country_prefix_01','phone_country_prefix_01',
                'phone_local_prefix_01','phone1','phone_country_prefix_02','phone_local_prefix_02',
                'phone2','fax_country_prefix','fax_local_prefix','fax','email_alt','organizations','user_type')
    
    organizations = make_ajax_field(UserProfile,'organizations','organization',help_text=('Enter text to search'),required=False)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(username=email).count():
            raise forms.ValidationError(_('Email addresses must be unique.'))
        return email

