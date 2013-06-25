from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdmin
from ecofunds.models import *
from ecofunds.opportunity.models import *
from ecofunds import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from ecofunds.user.models import UserProfile,UserType

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline , ]

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'acronym', 'state', 'type', 'created_at', 'validated']
    search_fields = ['name']
    list_filter = ['created_at']

    class Media:
        js = (settings.STATIC_URL+'tiny_mce/tiny_mce.js', settings.STATIC_URL+'tiny_mce/textareas.js')

class LocationAdmin(admin.ModelAdmin):
    class Media:
        js = (settings.STATIC_URL+'tiny_mce/tiny_mce.js', settings.STATIC_URL+'tiny_mce/textareas.js')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']
    fields = ['title', 'resume', 'description', 'image']
    
    class Media:
        js = (settings.STATIC_URL+'tiny_mce/tiny_mce.js', settings.STATIC_URL+'tiny_mce/textareas.js')

class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['recipient_organization', 'amount_usd', 'created_at']
    list_filter = ['created_at']

class ImageAdmin(admin.ModelAdmin):
    list_display = ['alt', 'position', 'plugin']

class UserTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(FundingOpportunity)
admin.site.register(Image, ImageAdmin)
admin.site.register(Location,LocationAdmin)
admin.site.unregister(User)
admin.site.register(User,UserProfileAdmin)
admin.site.register(UserType,UserTypeAdmin)
