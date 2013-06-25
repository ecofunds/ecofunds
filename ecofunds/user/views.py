from django.shortcuts import render_to_response
from ecofunds.user.models import *


def validate(request,user,code):
    try:
        mailv = MailValidation.objects.get(code=code)
    except MailValidation.DoesNotExist:
        return render_to_response('user/validation.html',{'validation_msg':'Unvalid code'})
    try:
        user = User.objects.get(pk=user)
    except User.DoesNotExist:
        return render_to_response('user/validation.html',{'validation_msg':'Unvalid user'})
    if mailv.user == user:
        mailv.validated = True
        mailv.save()
        u=user.get_profile()
        incomplete  = UserType.objects.get(name='incompleteuser')
        if u.user_type==incomplete:
            regularuser = UserType.objects.get(name='regularuser')
            u.user_type = regularuser
            u.save()
        return render_to_response('user/validation.html',{'validation_msg':'User validated!'})
    else:
        return render_to_response('user/validation.html',{'validation_msg':'Unvalid user'})
    
