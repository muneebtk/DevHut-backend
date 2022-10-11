from django.contrib import admin
from . models import Account
from django.contrib.auth.admin import UserAdmin


class AccountAdmin(UserAdmin):
    list_display = ('id','email','first_name','last_name','date_joined','is_active','followers')
    filter_horizontal = ()
    list_filter = ()
    list_display_links = ['first_name','email']
    ordering = ['id']
    readonly_fields = ('date_joined','last_login')
    fieldsets = ()
admin.site.register(Account,AccountAdmin)