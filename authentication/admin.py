from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import User, GroupProxy


admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = [
        "username",
        "email",
        "is_superuser",
        "is_staff"
    ]

    fieldsets = [
        [
            None, 
            {
                "fields": [
                    "username", 
                    "password"
                ]
            }
        ],
        [
            _("Personal info"),
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "email"
                ]
            }
        ],
        [
            _("Permissions"),
            {
                "fields": [
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions"
                ]
            }
        ],
        [
            _("Important dates"),
            {
                "fields": [
                    "last_login",
                    "date_joined"
                ]
            }
        ]
    ]

    search_fields = ["username", "first_name", "last_name", "email"]
    list_filter = [
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    ]
    

@admin.register(GroupProxy)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
