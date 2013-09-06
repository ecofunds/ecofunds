from django.views.generic import RedirectView
from django.core.urlresolvers import reverse


class Home(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        return reverse('map') + '#investment'
