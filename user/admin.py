from django.contrib import admin

from user.models import User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('balance',)
    list_display = ('username', 'email', 'balance', 'is_online')
    list_filter = ('is_active',)
    search_fields = ('username', 'email')


admin.site.register(User, UserAdmin)
