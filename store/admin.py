from django.contrib import admin

from store.models import (
    AccountObject,
    AccountsImage,
    BoostOrder,
    ChatRoom,
    Coupon,
    Message,
    Qualification,
    RPorder,
    SkinsOrder,
)


# Register your models here.

admin.site.register(Coupon)
admin.site.register(BoostOrder)
admin.site.register(Qualification)
admin.site.register(RPorder)
admin.site.register(ChatRoom)
admin.site.register(Message)


@admin.register(SkinsOrder)
class SkinOrderAdmid(admin.ModelAdmin):
    readonly_fields = ('created_at',)


class AccountsImageInLine(admin.TabularInline):
    model = AccountsImage
    extra = 1


@admin.register(AccountObject)
class AccountsAdmin(admin.ModelAdmin):
    inlines = [AccountsImageInLine]
