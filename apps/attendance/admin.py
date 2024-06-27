from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

# Register your models here.
class UserAdmin(BaseUserAdmin):
    list_display = ('username','email','is_staff')
    list_filter = ('is_superuser','is_staff','groups')
    fieldsets = (
        # (None, {'fields': ('username', 'password','email')}),
        # ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        # ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        # ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(Employee)
admin.site.register(Status)
admin.site.register(LeaveRequest)
admin.site.register(Attendance)
# admin.site.unregister(User)
# admin.site.register(User,UserAdmin)
