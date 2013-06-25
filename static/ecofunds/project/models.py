from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin, Page
from django.core import validators

class SearchProjectPlugin(CMSPlugin):
    page_result = models.ForeignKey(
                    Page,
                    verbose_name=_("Page result"),
                    blank=True,
                    null=True,
                    help_text=_("Link to result page.")
                  )

class DetailProjectPlugin(CMSPlugin):
    pass

class ProjectsPlugin(CMSPlugin):
    page_detail = models.ForeignKey(
                    Page,
                    verbose_name=_("Page detail"),
                    blank=True,
                    null=True,
                    help_text=_("Link to detail page.")
                  )
    card_limit = models.PositiveIntegerField(
        _('Number of news items to show'), 
        help_text=_('Limits the number of items that will be displayed')
    )

    table_limit = models.PositiveIntegerField(
        _('Number of news items to show'), 
        help_text=_('Limits the number of items that will be displayed')
    )

    def __unicode__(self):
        return ""

class ProjectFormPlugin(CMSPlugin):
    pass
