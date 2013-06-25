from ajax_select import LookupChannel
from ecofunds.models import *
from ecofunds.user.models import UserProfile
from django.contrib.auth.models import User
from django.db.models import Q

class OrganizationLookUp(LookupChannel):
    model = Organization
    search_field = 'name'
    def check_auth(self,request):
        pass

class LocationLookUp(LookupChannel):
    model = Location
    search_field = 'name'
    def get_query(self,q,request):
        return Location.objects.filter(Q(country__name__icontains=q)|Q(name__icontains=q))
    def check_auth(self,request):
        pass

class ActivityLookUp(LookupChannel):
    model = Activity
    search_field = 'name'
    def check_auth(self,request):
        pass

class UserProfileLookUp(LookupChannel):
    model = UserProfile
    def get_query(self,q,request):
        return UserProfile.objects.filter(user__username__icontains=q)
    def check_auth(self,request):
        pass

class ProjectLookUp(LookupChannel):
    model = Project
    search_field = 'title'
    def check_auth(self,request):
        pass

class CountryLookUp(LookupChannel):
    model = Country
    search_field = 'name'
    def check_auth(self,request):
        pass

class InvestmentLookUp(LookupChannel):
    model = Investment
    def get_query(self,q,request):
        return Investment.objects.filter(funding_organization__name__icontains=q)
    def get_result(self,obj):
        return u'%s %s %s'%(obj.funding_organization.name,obj.code,obj.amount)
    def check_auth(self,request):
        pass

