from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin, Page
from django.core import validators


class FundingOpportunity(CMSPlugin):
    page_detail = models.ForeignKey(
                    Page,
                    verbose_name=_("Page detail"),
                    blank=True,
                    null=True,
                    help_text=_("Link to detail page.")
            )
    limit = models.PositiveIntegerField(
                _('Number of news items to show'), 
                help_text=_('Limits the number of items that will be displayed')
            )

class DetailOpportunityPlugin(CMSPlugin):
    pass

class FundingOpportunityPlugin(CMSPlugin):
    page_detail = models.ForeignKey(
                    Page,
                    verbose_name=_("Page detail"),
                    blank=True,
                    null=True,
                    help_text=_("Link to detail page.")
                  )
    limit = models.PositiveIntegerField(
                _('Number of news items to show'), 
                help_text=_('Limits the number of items that will be displayed')
            )

    def __unicode__(self):
        return ""
