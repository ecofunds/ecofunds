
import os

from datetime import datetime, date
from django.db import models
from django.db.models import Max
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin, Page


def get_media_path(instance, filename):
    today = datetime.now()
    model = str(instance.__class__.__name__)
    return os.path.join(model,
            str(today.year), str(today.month), str(today.day), filename)

class Country(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = u'ecofunds_countries'
    def __unicode__(self):
        return self.name

class Attachment(models.Model):
    id = models.BigIntegerField(primary_key=True)
    path = models.FileField(_("File"), upload_to=get_media_path)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    #creater = models.ForeignKey(User, related_name='attachment_creaters')
    

    class Meta:
        db_table = u'ecofunds_attachments'
    def __unicode__(self):
        return self.name
    def save(self,*args,**kwargs):
        self.name = self.path.name
        super(Attachment,self).save(*args,**kwargs)

    def delete(self,*args,**kwargs):
        self.path.delete(False)
        super(Attachment,self).delete(*args,**kwargs)

class Activity(models.Model):
    activity_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = u'ecofunds_activities'
    def __unicode__(self):
        return self.name

class Currency(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    code = models.CharField(max_length=765)
    decimalnumbers = models.BigIntegerField()
    htmlsymbol = models.CharField(max_length=150, blank=True)
    ordering = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'ecofunds_currency'
    def __unicode__(self):
        return self.name

class CurrencyDefExchangeRate(models.Model):
    id = models.BigIntegerField(primary_key=True)
    currency = models.ForeignKey(Currency, null=True, blank=True)
    grant_year = models.IntegerField()
    rate = models.DecimalField(null=True, max_digits=20, decimal_places=9, blank=True)
    region = models.CharField(max_length=765)
    class Meta:
        db_table = u'ecofunds_currency_def_exchange_rate'

class CurrencyExchangeRate(models.Model):
    currency_exchange_rate_id = models.BigIntegerField(primary_key=True)
    currency_source = models.ForeignKey(Currency, null=True, blank=True, related_name='+')
    currency_target = models.ForeignKey(Currency, null=True, blank=True, related_name='+')
    grant_year = models.IntegerField()
    rate = models.DecimalField(null=True, max_digits=20, decimal_places=9, blank=True)
    region = models.CharField(max_length=765)
    class Meta:
        db_table = u'ecofunds_currency_exchange_rate'

class Geopoint(models.Model):
    geopoint_id = models.BigIntegerField(primary_key=True)
    
    #location = models.PointField() #PointField() # This field type is a guess.

    location_lat = models.DecimalField(blank=True, max_digits=18, decimal_places=16)
    location_lng = models.DecimalField(blank=True, max_digits=18, decimal_places=16)

    description = models.CharField(max_length=1524, blank=True)
    class Meta:
        db_table = u'ecofunds_geopoints'

class GeographicFocus(models.Model):
    id = models.BigIntegerField(primary_key=True)
    country = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'ecofunds_geographic_focus'

    
class OrganizationType(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=48)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'ecofunds_organization_type'

class Organization(models.Model):
    name = models.CharField(_('Name'), max_length=765)
    acronym = models.CharField(_('Acronym'), max_length=60, blank=True,null=True)
    mission = models.TextField(_('Description'), blank=True,null=True)
    grantmaker_type_id = models.BigIntegerField(null=True, blank=True)
    contact_salutation = models.CharField(max_length=75, blank=True,null=True)
    contact_first_name = models.CharField(max_length=150, blank=True,null=True)
    contact_last_name = models.CharField(max_length=150, blank=True,null=True)
    contact_title = models.CharField(max_length=150, blank=True,null=True)

    country = models.ForeignKey(Country)
    toolkit = models.CharField(max_length=140,null=True,blank=True)
    political_divition_id = models.BigIntegerField(null=True, blank=True)
    street1 = models.CharField(max_length=765, blank=True,null=True)
    street2 = models.CharField(max_length=765, blank=True,null=True)
    city = models.CharField(max_length=150, blank=True,null=True)
    zip = models.CharField(max_length=60, blank=True,null=True)
    state = models.ForeignKey('Location')
    phone_country_prefix = models.CharField(max_length=3, blank=True,null=True)
    phone_local_prefix = models.CharField(max_length=30, blank=True,null=True)
    phone_number = models.CharField(max_length=30, blank=True,null=True)
    fax_country_prefix = models.CharField(max_length=15, blank=True,null=True)
    fax_local_prefix = models.CharField(max_length=30, blank=True,null=True)
    fax_number = models.CharField(max_length=30, blank=True,null=True)
    email = models.CharField(max_length=450, blank=True,null=True)
    url = models.CharField(max_length=765, blank=True,null=True)
    activities_other = models.CharField(max_length=765, blank=True,null=True)
    logo = models.CharField(max_length=765, blank=True,null=True)
    userprofiles = models.ManyToManyField('user.UserProfile',through='user.UserProfileOrganization',blank=True,null=True)
    #desired_location = models.PointField(blank=True) # PointField(blank=True) # This field type is a guess.

    desired_location_lat = models.DecimalField(blank=True,null=True, max_digits=19, decimal_places=16)
    desired_location_lng = models.DecimalField(blank=True,null=True, max_digits=19, decimal_places=16)

    desired_location_text = models.CharField(max_length=765, blank=True,null=True)
    created_at = models.DateTimeField(_('Created at'), null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    creater = models.ForeignKey(User, null=True, blank=True, related_name='+')
    updater = models.ForeignKey(User, null=True, blank=True, related_name='+')
    validated = models.BooleanField(default=0)
    type = models.ForeignKey(OrganizationType, null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to=get_media_path,null=True,blank=True)
    website = models.CharField(max_length=150,blank=True,null=True)
    active = models.BooleanField(default=1)

    projects = models.ManyToManyField('Project', through='ProjectOrganization',
            related_name='projects_by_org',blank=True,null=True)

    def funding_investments():
        return Investment.all_objects.filter(Q(funding_organization=self.id))
    
    def received_investments():
        return Investment.all_objects.filter(Q(recipient_organization=self.id))
    
    def get_year_recipient_investments(self):
        now = datetime.now()
        return self.recipient_investments.all().filter(created_at__year=now.year)

    def get_current_investment(self):
        investments = self.recipient_investments.order_by('-created_at')
        return investments[0] if investments.count() > 0 else None

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'ecofunds_organization'


class OrganizationAttachment(models.Model):
    organization = models.ForeignKey(Organization, primary_key=True, related_name='organizations_attachments')
    attachment = models.ForeignKey(Attachment, primary_key=True, related_name='organizations_attachments')

    class Meta:
        db_table = u'ecofunds_organization_attachments'
        unique_together = ('organization','attachment')


class Location(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    
    country = models.ForeignKey(Country, related_name='locations')

    iso_code = models.CharField(max_length=10)
    iso_cc = models.CharField(max_length=10)
    iso_sub = models.CharField(max_length=10)
    admintype = models.CharField(max_length=200)
    disputed = models.BooleanField()
    autonomous = models.BooleanField()
    continent = models.CharField(max_length=50)
    shape_length = models.FloatField()
    polygon = models.TextField()

    projects = models.ManyToManyField('Project', through='ProjectLocation')

    class Meta:
        db_table = u'ecofunds_locations'
    def __unicode__(self):
        if self.country:
            return unicode(self.country)+'/'+unicode(self.name)
        else:
            return self.name

class Project(models.Model):

    entity_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255,unique=True)
    acronym = models.CharField(_('Acronym'), max_length=60, blank=True)
    resume = models.CharField(max_length=150)
    grant_year = models.IntegerField()
    grant_from = models.DateTimeField(null=True, blank=True)
    grant_to = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True, blank=True)
    creater = models.ForeignKey(User, related_name='+')
    updater = models.ForeignKey(User, null=True, blank=True, related_name='+')
    validated = models.IntegerField(null=True, blank=True)
    is_project = models.IntegerField(null=True, blank=True)

    image = models.ImageField(_("Image"), upload_to=get_media_path,null=True,blank=True)

    currency = models.ForeignKey(Currency, null=True, blank=True)
    budget = models.DecimalField(_('Budget'), null=False, max_digits=20, decimal_places=2, blank=False)
    organization = models.ManyToManyField(Organization,through=Organization.projects.through,related_name='organizations_set')
    main_organization = models.ForeignKey(Organization,related_name="main_org")
    activity_description = models.TextField(blank=True)
    activities = models.ManyToManyField('Activity',through='ProjectActivity',related_name='activities')
    locations = models.ManyToManyField(Location,through=Location.projects.through,related_name="location_project")
    phone_country_prefix_01 = models.CharField(max_length=3, blank=True,null=True)
    phone_local_prefix_01 = models.CharField(max_length=30, blank=True,null=True)
    phone_number_01 = models.CharField(_('Phone number 01'),max_length=20,blank=True,null=True)
    phone_country_prefix_02 = models.CharField(max_length=3, blank=True,null=True)
    phone_local_prefix_02 = models.CharField(max_length=30, blank=True,null=True)
    phone_number_02 = models.CharField(_('Phone number 02'),max_length=20,blank=True,null=True)
    fax_country_prefix = models.CharField(max_length=3, blank=True,null=True)
    fax_local_prefix = models.CharField(max_length=30, blank=True,null=True)
    fax = models.CharField(_('FAX'),max_length=20,blank=True,null=True)
    website = models.CharField(max_length=150,blank=True,null=True)
    active = models.BooleanField(default=1)
    sub_projects = models.ManyToManyField('Project',through='ProjectXProject',blank=True,null=True)
    email = models.CharField(max_length=350, blank=True,null=True)

    def get_year_recipient_investments(self):
        now = datetime.now()
        return self.recipient_investments.filter(created_at__year=now.year)

    def get_current_investment(self):
        investments = self.recipient_investments.order_by('-created_at')
        return investments[0] if investments.count() > 0 else None

    def get_firstlocation(self):
        
        return self.projects_locations.all()[:1].get() if self.projects_locations.count() > 0 else None

    def __unicode__(self):
        return self.title

    def is_completed(self):
        return self.grant_to >= datetime.now()

    class Meta:
        db_table = u'ecofunds_entities'
    def save(self,*args,**kwargs):
        if self.grant_from:
            self.grant_year = self.grant_from.year
        self.created_at = datetime.now()
        super(Project,self).save(*args,**kwargs)

class ProjectXProject(models.Model):
    parent_project = models.ForeignKey('Project',related_name='children_projects')
    child_project = models.ForeignKey('Project',related_name='father_projects')
    class Meta:
        unique_together=('parent_project','child_project')

class ProjectAttachment(models.Model):
    entity = models.ForeignKey(Project, primary_key=True, related_name='attachments')
    attachment = models.ForeignKey(Attachment, primary_key=True, related_name='projects')

    class Meta:
        db_table = u'ecofunds_entity_attachments'
        unique_together=('entity','attachment')

class ProjectLocation(models.Model):
    entity = models.ForeignKey(Project, primary_key=True, related_name='projects_locations')
    location = models.ForeignKey(Location, primary_key=True)
    class Meta:
        db_table = u'ecofunds_entity_locations'
        unique_together=('entity','location')

class ProjectActivity(models.Model):
    entity = models.ForeignKey(Project, primary_key=True, related_name='projects_activities')
    activity = models.ForeignKey(Activity)
    class Meta:
        db_table = u'ecofunds_entity_activities'
        unique_together=('entity','activity')

class ProjectGeographicfocus(models.Model):
    entity = models.ForeignKey(Project, primary_key=True)
    geographic_focus = models.ForeignKey(GeographicFocus)
    class Meta:
        db_table = u'ecofunds_entity_geographicfocus'
        unique_together=('entity','geographic_focus')

class ProjectGeopoint(models.Model):
    entity = models.ForeignKey(Project, primary_key=True)
    geopoint = models.ForeignKey(Geopoint)
    class Meta:
        db_table = u'ecofunds_entity_geopoints'
        unique_together = ('entity','geopoint')

class ProjectOrganization(models.Model):
    entity = models.ForeignKey(Project, related_name='organizations')
    organization = models.ForeignKey(Organization, related_name='projects_organizations')
    main = models.BooleanField()
    class Meta:
        db_table = u'ecofunds_entity_organizations'
        unique_together=('entity','organization')

class InvestmentType(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    
    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'ecofunds_investment_types'

class Investment(models.Model):
    id = models.AutoField(primary_key=True)
    recipient_entity = models.ForeignKey(Project,null=True,blank=True,related_name='recipient_investments')
    funding_entity = models.ForeignKey(Project,null=True,blank=True,related_name='funding_investments')
    recipient_organization = models.ForeignKey(Organization, related_name='recipient_investments')
    funding_organization = models.ForeignKey(Organization, blank=True,null=True ,related_name='funding_investments')
    
    currency = models.ForeignKey(Currency, null=True, blank=True)
    amount = models.DecimalField(_('Amount'), null=True, max_digits=20, decimal_places=2, blank=True)
    amount_usd = models.DecimalField(_('Amount (USD)'), null=True, max_digits=20, decimal_places=2, blank=True)
    created_at = models.DateTimeField(_('Created at'), null=True, blank=True)
    updated_at = models.DateTimeField(_('Updated at'), null=True, blank=True)
    source_inverstiment = models.ForeignKey('self', null=True, blank=True, related_name='+')
    date = models.DateField()
    estimated_completion = models.DateField()
    type = models.ForeignKey(InvestmentType, null=True, blank=True)
    code = models.CharField(max_length=20)
    active = models.BooleanField(default=1)
    investment_flow = models.ManyToManyField('Investment',null=True,blank=True,through='InvestmentFlow')
    class Meta:
        db_table = u'ecofunds_investments'
        verbose_name = _('Investment')
        verbose_name_plural = _('Investments')
        ordering = ('-created_at', )

    def __radd__(self, other):
        return other + self.amount_usd
    def save(self,*args,**kwargs):
        if not self.code:
            start = self.funding_organization.name[:3].upper()
            end = self.recipient_organization.name[:3].upper()
            t = self.type.pk
            dat=datetime.now().strftime("%Y-%m-%d")
            self.code="%s-%s-%s-%s"%(dat,t,start,end)
        super(Investment,self).save(*args,**kwargs)
    def __unicode__(self):
        return self.code

class InvestmentAttachment(models.Model):
    investment = models.ForeignKey(Investment, primary_key=True, related_name='attachments')
    attachment = models.ForeignKey(Attachment, primary_key=True, related_name='investments')

    class Meta:
        db_table = u'ecofunds_investment_attachments'
        unique_together = ('investment','attachment')

class UicnCatalog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    class Meta:
        db_table = u'ecofunds_uicn_catalog'


class ListImagePlugin(CMSPlugin):
    limit = models.PositiveIntegerField(
                _('Number of news items to show'), 
                help_text=_('Limits the number of items that will be displayed')
            )
    
    def __unicode__(self):
        str = ""
        if self.page:
            str +=  _("Page")+": %s [%s]" % (self.page.get_title(), self.language)

        if self.placeholder:
            if len(str) > 0 :
                str += ", "
            str += _("Placeholder")+(": %s [%d]" % (self.placeholder.slot, self.position))

        return str

class Image(models.Model):
    """
    A Picture with or without a link
    """
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    FLOAT_CHOICES = ((CENTER, _("center")),
                     (LEFT, _("left")),
                     (RIGHT, _("right")),
                     )
    
    
    image = models.ImageField(_("image"), upload_to=get_media_path,null=True,blank=True)
    url = models.CharField(_("link"), max_length=255, blank=True, null=True, help_text=_("if present image will be clickable"))
    page_link = models.ForeignKey(Page, verbose_name=_("page"), null=True, blank=True, help_text=_("if present image will be clickable"))
    alt = models.CharField(_("alternate text"), max_length=255, blank=True, null=True, help_text=_("textual description of the image"))
    longdesc = models.CharField(_("long description"), max_length=255, blank=True, null=True, help_text=_("additional description of the image"))
    float = models.CharField(_("side"), max_length=10, blank=True, null=True, choices=FLOAT_CHOICES)
    
    position = models.PositiveSmallIntegerField(_("position"), blank=True, null=True)

    plugin = models.ForeignKey(ListImagePlugin, null=False, blank=False, related_name='images')

    class Meta:
        db_table = u'ecofunds_images'

    

    def __unicode__(self):
        if self.alt:
            return self.alt[:40]
        elif self.image:
            # added if, because it raised attribute error when file wasn't defined
            try:
                return u"%s" % basename(self.image.path)
            except:
                pass
        return "<empty>"

class NotificationType(models.Model):
    id = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=150,blank=True,null=True,unique=True)
    def __unicode__(self):
        return self.description

class Notification(models.Model):
    id = models.BigIntegerField(primary_key=True)
    #Usuarios que devem receber a notificacao
    users_reader = models.ManyToManyField(User,through='NotificationReader',related_name="users_readers")
    notification_type = models.ForeignKey(NotificationType)
    #objetos ao qual a notificacao faz referencia
    user = models.ForeignKey(User,blank=True,null=True,related_name="user_owner")
    organization = models.ForeignKey(Organization,blank=True,null=True)
    project = models.ForeignKey(Project,blank=True,null=True)
    user_updated = models.ForeignKey(User,blank=True,null=True,related_name='update_notes')
    inserted_date = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True)
    def __unicode__(self):
        return self.message
    class Meta:
        db_table = u'ecofunds_notifications'

class InvestmentFlow(models.Model):
    father = models.ForeignKey(Investment,related_name='supported_investments')
    child = models.ForeignKey(Investment,related_name='children_investments')
    class Meta:
        unique_together = ('father','child')

class NotificationReader(models.Model):
    reader = models.ForeignKey(User,primary_key=True,related_name='users_notification')
    notification = models.ForeignKey(Notification,related_name='project_notification')
    readed_date = models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together=('reader','notification')

class AttachmentType(models.Model):
    name = models.CharField(unique=True,max_length=80)
    def __unicode__(self):
        return self.name

class AttachmentPlugin(CMSPlugin):
    model = models.ForeignKey(AttachmentType)
    def __unicode__(self):
        return u'attachment %s'%self.model
