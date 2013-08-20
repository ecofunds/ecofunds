# coding: utf-8
from django import forms
from django.utils.translation import gettext as _
from ecofunds.core.models import OrganizationType
from ecofunds.maps.forms.widgets import GoogleMap


class MapForm(forms.Form):

    map = forms.Field(widget=GoogleMap(attrs={
            'nojquery': True,
            'nostaticimage': True,
            'width':100,
            'width_pixels':False,
            'height':370,
            'height_pixels':True,
        }))

    def __init__(self, *args, **kwargs):
        super(MapForm, self).__init__(*args, **kwargs)
        

        map = self.fields['map']
        if kwargs.has_key('initial'):
            for key, value in kwargs.get('initial').iteritems():
                if key != 'map':
                    if self.fields['map'].widget.attrs.has_key(key):
                        self.fields['map'].widget.attrs[key] = value
                    else:
                        self.fields['map'].widget.attrs.update({key:value})


class MapFilterForm(forms.Form):
    name = forms.CharField(required=False)
    kind = forms.ModelChoiceField(queryset=OrganizationType.objects.all(), required=False, empty_label=_('Choose an organization type'))
    country = forms.CharField(required=False)
    state = forms.CharField(required=False)

