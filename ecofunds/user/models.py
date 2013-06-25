
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, UserManager,Permission
from django.utils.translation import ugettext_lazy as _

from ecofunds.models import *
from cms.models import CMSPlugin, Page
from django.core.mail import send_mail
from ecofunds.settings import VALIDATE_EMAIL_URL
from ecofunds.user.notification import create_notification_type

import uuid

class UserType(models.Model):
    name = models.CharField(max_length=80,unique=True)
    permissions = models.ManyToManyField(Permission,blank=True,null=True)
    def __unicode__(self):
        return self.name

class UserProfile(models.Model):
    #Campo necessario
    user = models.OneToOneField(User)
    organizations = models.ManyToManyField('ecofunds.Organization',null=True,through='UserProfileOrganization')
    title = models.CharField(max_length=80,blank=True,null=True)
    country = models.ForeignKey('ecofunds.Country',blank=True,null=True)
    phone_country_prefix_01 = models.CharField(max_length=3, blank=True,null=True)
    phone_local_prefix_01 = models.CharField(max_length=30, blank=True,null=True)
    phone1 = models.CharField(max_length=15,blank=True,null=True)
    phone_country_prefix_02 = models.CharField(max_length=3, blank=True,null=True)
    phone_local_prefix_02 = models.CharField(max_length=30, blank=True,null=True)
    phone2 = models.CharField(max_length=15,blank=True,null=True)
    fax_country_prefix = models.CharField(max_length=3, blank=True,null=True)
    fax_local_prefix = models.CharField(max_length=30, blank=True,null=True)
    fax = models.CharField(max_length=15,blank=True,null=True)
    website = models.CharField(max_length=80,blank=True,null=True)
    aim = models.CharField(max_length=80,blank=True,null=True)
    user_type = models.ForeignKey(UserType,null=True)   
    email_alt = models.CharField(max_length=80,null=True,blank=True)
    image = models.ImageField(_("image"), upload_to=get_media_path,null=True,blank=True)
    active = models.BooleanField(default=1)
    def __unicode__(self):
        return unicode(self.user)
    def has_permission(self,codename):
        if self.user.is_superuser:
            return True
        if self.user_type:
            has = self.user_type.permissions.filter(codename=codename)
            if has:
                return has
        return False
    def has_permissions(self,codenames):
        if self.user.is_superuser:
            return True
        if self.user_type:
            has = self.user_type.permissions.filter(codename__in=codenames)
            if has:
                return has
        return False
    
    def can_ownedit(self,obj):
        """verifica se foi criado pelo usuario,
        se sim, ele tem permissao ao objeto"""
        if isinstance(obj, Organization):
            if obj.creater==self.user:
                return True
            else:
                return False
        elif isinstance(obj,Project):
            if obj.creater==self.user:
                return True
            else:
                return False
        elif isinstance(obj,UserProfile):
            if obj.pk == self.pk:
                return True
            else:
                return False
        else:
            return False

    def can_orgedit(self,obj):
        """verifica se o obj eh de uma organizacao que o usuario eh
        administrador. se sim, ele tem permissao ao objeto"""
        if isinstance(obj, Organization):
            #verifica se eh administrador da organizacao
            userorg =  UserProfileOrganization.objects.filter(organization=obj.pk,userprofile=self)
            if not userorg:
                return False
            userorg = userorg[0]
            if userorg.admin or userorg.organization.creater==self.user.pk:
                return True
            else:
                return False
        elif isinstance(obj,Project):
            orgs = ProjectOrganization.objects.filter(organization__in=self.organizations.filter(admin=True),entity=obj.pj)
            if org:
                return True
            else:
                return False
        elif isinstance(obj,Investment):
            try:
                org = self.organizations.get(organization=obj.pk)
            except Organization.DoesNotExist:
                return False
            if org.pk == obj.recipient_organization or org.pk == obj.funding_organization:
                return True
            else:
                return False
        elif isinstance(obj,UserProfile):
            if obj.pk == self.pk:
                return True
            org = obj.organizations.filter(organization__in=self.organizations.filter(admin=True))
            if org:
                return True
            else:
                return False
        else:
            return False

    def can_regionedit(self,obj):
        """Verifica se o objeto pertence a uma localizacao
        a qual o usuario eh ponto focal, se sim ele tem permissao
        ao objeto"""
        if isinstance(obj,Organization):
            if obj.country == self.country:
                return True
            try:
                org = self.organizations.get(organization=obj.pk)
            except Organization.DoesNotExist:
                return False
            if org.admin or org.creater == self.user.pk:
                return True
            else:
                return False
        elif isinstance(obj,Project):
            try:
                projloc = ProjectLocation.objects.get(pk=obj.pk)
            except ProjectLocation.DoesNotExist:
                orgs = ProjectOrganization.objects.filter(organization__in=self.organizations.filter(admin=True),entity=obj.pj)
                if org:
                    return True
                else:
                    return False
            if projloc.location.country == self.country:
                return True
            else:
                return False
        elif isinstance(obj,Investment):
            if obj.recipient_organization.country==self.country or obj.funding_organization.country==self.country:
                return True
            else:
                try:
                    org = self.organizations.get(organization=obj.pk)
                except Organization.DoesNotExist:
                    return False
                if org.pk == obj.recipient_organization or org.pk == obj.funding_organization:
                    return True
                else:
                    return False
        elif isinstance(obj,UserProfile):
            if obj.country == self.country:
                return True
            else:
                org = obj.organizations.filter(organization__in=self.organizations.filter(admin=True))
                if org:
                    return True
                else:
                    return False
        else:
            return False

    def is_allowed(self,obj,type='change'):
        #type pode ser add,change,delete,orgedit,ownedit ,regionedit
        #talvez precise de algo como owndelete, ver.
        if self.user.is_superuser:
            return True
        content_type = get_content_type(obj)
        perm_code = "%s_%s"%(type,content_type.model)
        print 'perm_code : %s'%perm_code
        has =  self.has_permission(perm_code)
        if has:
            print 'has'
            if type in ('add','change','delete'):
                #essas permissoes sao Model based
                #entao, se ele as tem, tem para todas 
                #instancias do modelo
                return True
            else:
                #se nao for o caso, precisamos verificar
                #permissoes object based, seguindo as 
                #regras de negocio estipuladas
                if type=='ownedit':
                    return self.can_ownedit(obj)
                elif type=='regionedit':
                    return self.can_regionedit(obj)
                elif type=='orgedit':
                    return self.can_orgedit(obj)
                else:
                    raise ValueError("esse tipo de permissao %s nao esta definido"%type)
        else: 
            return False
    #em templates, eh util para saber se deve mostrar um conjunto de edicoes ou nao
    def can_edit(self,obj,permissions=('change','delete','ownedit','orgedit','regionedit')):
        if self.user.is_superuser:
            return True
        content_type = get_content_type(obj)
        modelname = content_type.model
        perm_codes = ['%s_%s'%(p,modelname) for p in permissions]
        has = self.has_permissions(perm_codes)
        if has:
            return True
        else:
           return False
    def save(self,*args,**kwargs):
        out = super(self.__class__,self).save(*args,**kwargs)
        if self.user_type and self.user_type.name=='superadmin':
            self.user.is_superuser = True
            self.user.save()
        return out

    

class UserProfileProjects(models.Model):
    userprofile = models.ForeignKey(UserProfile,related_name='userprofile_id_project')
    project = models.ForeignKey('ecofunds.Project',related_name='project_id')
    class Meta:
        unique_together=('userprofile','project')

class UserProfileOrganization(models.Model):
    userprofile = models.ForeignKey(UserProfile,related_name='userprofile_id_organization')
    organization = models.ForeignKey('ecofunds.Organization',related_name='organ')
    admin = models.BooleanField()
    class Meta:
        unique_together=('userprofile','organization')

class MailValidation(models.Model):
    user = models.OneToOneField(User)
    code = models.CharField(max_length=60,blank=False,unique=True)
    validated = models.BooleanField(blank=True)
    def save(self,*args,**kwargs):
        if not self.code:
            self.code = unicode(uuid.uuid1()).replace('-','')
        return super(MailValidation,self).save(*args,**kwargs)
    def validate(self,code):
        try:
            MailValidation.objects.get(code=code)
        except MailValidation.DoesNotExist:
            return False
        self.validated = True
        self.save()
        return True
    def send_validation(self,address):
        subject = 'New account at ecofunds'
        msg = 'Click in the link below to create your new user on ecofunds %s%s/%s/'%(VALIDATE_EMAIL_URL,self.user.pk,self.code)
        send_mail(subject,msg,address,[address],fail_silently=False)

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

class UserFormPlugin(CMSPlugin):
    self_user = models.BooleanField()

class NotificationPlugin(CMSPlugin):
    pass

class UserDetailPlugin(CMSPlugin):
    pass

from ecofunds.user.permissions import create_permissions,get_content_type,relate_user_type


#tenta salvar permissoes e tipos de usuarios.
#porem, caso as tabelas nao estejam syncadas, pode resultar em erro
#create_notification_type()
create_permissions()
relate_user_type()

