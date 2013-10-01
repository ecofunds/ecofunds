from django.contrib import admin
from ecofunds import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from ecofunds.user.models import UserProfile, UserType
from ecofunds.core.models import (Organization, Project, Investment, Image, Location, ProjectLocation, Country,
                                  Attachment, Activity, Currency, OrganizationType, OrganizationAttachment,
                                  ProjectXProject, ProjectAttachment, ProjectActivity, ProjectOrganization,
                                  InvestmentType, InvestmentAttachment, ListImagePlugin, NotificationType, Notification,
                                  InvestmentFlow, NotificationReader, AttachmentType, AttachmentPlugin)


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
    list_filter = ['country']

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


# admin.site.register(Organization, OrganizationAdmin)
# admin.site.register(Project, ProjectAdmin)
# admin.site.register(Investment, InvestmentAdmin)
# admin.site.register(Image, ImageAdmin)
# admin.site.register(Location,LocationAdmin)
# admin.site.unregister(User)
# admin.site.register(User,UserProfileAdmin)
# admin.site.register(UserType,UserTypeAdmin)
# admin.site.register(ProjectLocation)
#
#
# admin.site.register(Country)
# admin.site.register(Attachment)
# admin.site.register(Activity)
# admin.site.register(Currency)
# admin.site.register(OrganizationType)
# admin.site.register(OrganizationAttachment)
# admin.site.register(ProjectXProject)
# admin.site.register(ProjectAttachment)
# admin.site.register(ProjectActivity)
# admin.site.register(ProjectOrganization)
# admin.site.register(InvestmentType)
# admin.site.register(InvestmentAttachment)
# admin.site.register(ListImagePlugin)
# admin.site.register(NotificationType)
# admin.site.register(Notification)
# admin.site.register(InvestmentFlow)
# admin.site.register(NotificationReader)
# admin.site.register(AttachmentType)
# admin.site.register(AttachmentPlugin)
