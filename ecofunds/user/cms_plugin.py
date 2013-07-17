from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from ecofunds.core.models import *
from ecofunds.user.models import *
from ecofunds.user.forms import *

from django.http import Http404
from django.contrib.auth.models import User


class CMSUserFormPlugin(CMSPluginBase):
    model = UserFormPlugin
    name = _("User Form")
    render_template = "user/form.html"
    module = _("User")

    def render(self,context,instance,placeholder):
        request = context['request']
        if request.method=='POST':
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    user = UserProfile.objects.get(pk=pk_id)
                    if instance.selfuser:
                        userform = SelfUserForm(request.Post,instance=user)
                    userform.updater = request.user
                except UserProfile.DoesNotExist:
                    if instance.selfuser:
                        raise Http404
            else:
                userform = SelfUserForm(request.POST)
            if userform.is_valid():
                u =userform.save(commit=False)
                if not u.pk:
                    user = User()
                else:
                    user = u.user
                username = userform.cleaned_data.get('username')
                password = userform.cleaned_data.get('password')
                check_password = userform.cleaned_data.get('check_password')
                first_name = userform.cleaned_data.get('first_name')
                last_name = userform.cleaned_data.get('last_name')
                email = userform.cleaned_data.get('email')
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.set_password(password)
                user.save()
                sendmail=False
                if not u.pk:
                    u = user.get_profile()
                    unvalidateduser = UserType.objects.get(name='incompleteuser')
                    u.user_type = unvalidateduser
                    sendmail=True
                u.save()
                if sendmail:
                    mvalidate=MailValidation(user=user)
                    mvalidate.save()
                    mvalidate.send_validation(user.email)
            else:
                context.update({'formset':userform})
                return context
        else:
            if request.GET.has_key('id'):
                pk_id = request.GET['id']
                try:
                    user = self.UserProfile.objects.get(pk=pk_id)
                except UserProfile.DoesNotExist:
                    if instance.self_user:
                        context.update({'formset':SelfUserForm()})
                        return context
            else:
                context.update({'formset':SelfUserForm()})
                return context

plugin_pool.register_plugin(CMSUserFormPlugin)
