from django import forms
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