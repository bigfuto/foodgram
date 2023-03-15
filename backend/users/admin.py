from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Subscription


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'is_active')
        }),
    )
    list_display = ('username', 'email', 'first_name', 'is_active',)
    search_fields = ('first_name', 'email')
    list_filter = ('first_name', 'email',)
    empty_value_display = '-пусто-'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')
    search_fields = ('author', 'subscriber')
    list_filter = ('author', 'subscriber')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
