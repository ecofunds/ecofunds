from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from ecofunds.models import *
from ecofunds.user.notification import notificate
from ecofunds.user.models import *
from ecofunds.user.forms import *
from permissions import edit_allowance
from ecofunds.middleware.forcedresponse import ForceResponse
from django.http import HttpResponseRedirect

from datetime import datetime

from django.http import Http404
from django.contrib.auth.models import User
from django.utils.translation import get_language
from django.db.models import Q

class CMSUserFormPlugin(CMSPluginBase):
    model = UserFormPlugin
    name = _("User Form")
    render_template = "user/form.html"
    module = _("User")
    redirect_language = {'pt-br':'../ficha-usuario',
            'en':'../user-detail',
            'es':'../ficha-usuario',
            }

    def render(self,context,instance,placeholder):
        request = context['request']
        if request.method=='POST':
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    user = UserProfile.objects.get(pk=pk_id)
                    userform = UserForm(request.POST,request.FILES,instance=user)
                    note_type="update"
                    userform.updater = request.user
                except UserProfile.DoesNotExist:
                    if instance.self_user:
                        raise Http404
            else:
                userform = UserForm(request.POST,request.FILES)
                note_type="create"
            if userform.is_valid():
                u =userform.save(commit=False)
                if not u.pk:
                    user = User()
                else:
                    user = u.user
                username = userform.cleaned_data.get('email')
                password = userform.cleaned_data.get('password')
                check_password = userform.cleaned_data.get('check_password')
                first_name = userform.cleaned_data.get('first_name')
                last_name = userform.cleaned_data.get('last_name')
                email = userform.cleaned_data.get('email')
                phone_country_prefix_01 = userform.cleaned_data.get('phone_country_prefix_01')
                phone_local_prefix_01 = userform.cleaned_data.get('phone_local_prefix_01')
                phone1 = userform.cleaned_data.get('phone1')
                phone_country_prefix_02 = userform.cleaned_data.get('phone_country_prefix_02')
                phone_local_prefix_02 = userform.cleaned_data.get('phone_local_prefix_02')
                phone2 = userform.cleaned_data.get('phone2')
                fax_country_prefix = userform.cleaned_data.get('fax_country_prefix')
                fax_local_prefix = userform.cleaned_data.get('fax_local_prefix')
                fax = userform.cleaned_data.get('fax')
                email_alt = userform.cleaned_data.get('email_alt')
                title = userform.cleaned_data.get('title')
                user_type = userform.cleaned_data.get('user_type')
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.set_password(password)
                user.save()
                u.user = user
                sendmail=False
                if not u.pk:
                    #como precisa dessa linha, vai precisar pegar todos campos manualmente
                    #sem contar com o modelform
                    u = user.get_profile()
                    if instance.self_user:
                        unvalidateduser = UserType.objects.get(name='incompleteuser')
                        u.user_type = unvalidateduser
                        sendmail=True
                u.phone_country_prefix_01=phone_country_prefix_01
                u.phone_local_prefix_01 = phone_local_prefix_01
                u.phone1 = phone1
                u.user_type = user_type
                u.phone_country_prefix_02=phone_country_prefix_02
                u.phone_local_prefix_0 = phone_local_prefix_02
                u.phone2 = phone2
                u.fax_country_prefix = fax_country_prefix
                u.fax_local_prefix = fax_local_prefix
                u.fax = fax
                u.email_alt = email_alt
                u.title = title
                u.save()
                if userform.cleaned_data.get('organizations'):
                    for orgid in userform.cleaned_data.get('organizations'):
                        obj = Organization.objects.get(pk=orgid)
                        userorg = UserProfileOrganization(userprofile=u,
                                organization=obj)
                        try:
                            userorg.save()
                        except IntegrityError:
                            pass
                if sendmail:
                    mvalidate=MailValidation(user=user)
                    mvalidate.save()
                    mvalidate.send_validation(userform.cleaned_data.get('email'))
                if request.user.is_authenticated:
                    notificate(u,note_type,request.user,'teste')
                else:
                    notificate(u,note_type,u,'teste')
                context.update({'redirect':u.pk})
                lang = get_language()
                redirect_url = self.redirect_language[lang]
                raise ForceResponse(HttpResponseRedirect(redirect_url+'?id=%s'%u.pk))
            else:
                context.update({'formset':userform})
                return context
        else:
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    user = UserProfile.objects.get(pk=pk_id)
                except UserProfile.DoesNotExist:
                    if instance.self_user:
                        userform = UserForm()
                        context.update({'formset':userform})
                        return context
            else:
                userform = UserForm()
                context.update({'formset':userform})
                return context


class CMSNotificationPlugin(CMSPluginBase):    
    model = NotificationPlugin
    name = _("Notifications")
    render_template = "user/notelist.html"
    module=_("User")

    def render(self,context,instance,placeholder):
        request = context['request']
        user = request.user
        notes = NotificationReader.objects.filter(reader=user)
        out = []
        for note in notes:
            out.append(note.notification)
            note.readed_date = datetime.now()
        context.update( {"notifications":out} ) 
        return context

class CMSDetailUserPlugin(CMSPluginBase):
    model = UserDetailPlugin
    name = _("User Detail")
    render_template = "user/detail.html"
    module = _("User")

    def render(self, context, instance, placeholder):
        request = context['request']
        id = request.GET.get('id')
        try:
            userprofile = UserProfile.objects.get(pk=id)
        except UserProfile.DoesNotExist:
            return context
        perm = False
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except UserProfile.DoesNotExist:
                profile = None
            if profile:
                perm = edit_allowance(userprofile,profile)
        orgsdetail  = userprofile.organizations.all()
        sameorgs = UserProfile.objects.filter(organizations__in=orgsdetail).exclude(user__username=userprofile.user.username)
        #ver projetos da organizacao
        projs = Project.objects.filter(Q(organization__in=orgsdetail)|Q(main_organization__in=orgsdetail))
        #ver que organziacoes estao neles
        otherorgs = []
        for proj in projs:
            otherorgs.append(proj.main_organization)
            for porg in proj.organizations.all():
                otherorgs.append(porg)
        #ver que usuarios estao nelas
        sameprojs = UserProfileOrganization.objects.filter(organization__in=otherorgs).exclude(userprofile=userprofile)
        sameprojs = [i.userprofile for i in sameprojs]
        context.update({
            'organizations':orgsdetail,
            'same_organizations':sameorgs,
            'same_projects':sameprojs,
            'userprofile': userprofile,
            'instance':instance,
            'placeholder':placeholder,
            'perm':perm,
        })
        return context

plugin_pool.register_plugin(CMSUserFormPlugin)
plugin_pool.register_plugin(CMSNotificationPlugin)
plugin_pool.register_plugin(CMSDetailUserPlugin)
