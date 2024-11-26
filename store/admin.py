from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from store.models import (
    AccountObject,
    AccountOrder,
    AccountsImage,
    BoostOrder,
    ChatRoom,
    Coupon,
    Message,
    Qualification,
    ReviewSellerModel,
    RPorder,
    SkinsOrder,
)


# Register your models here.

admin.site.register(Coupon)
admin.site.register(Qualification)
admin.site.register(RPorder)
admin.site.register(ChatRoom)
admin.site.register(AccountOrder)


@admin.register(BoostOrder)
class BoostOrderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'created_at']
    readonly_fields = ('created_at',)


@admin.register(SkinsOrder)
class SkinOrderAdmid(admin.ModelAdmin):
    readonly_fields = ('created_at',)


class AccountsImageInLine(admin.TabularInline):
    model = AccountsImage
    extra = 1


@admin.register(AccountObject)
class AccountsAdmin(admin.ModelAdmin):
    inlines = [AccountsImageInLine]


class MessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'massage_type')


admin.site.register(Message, MessageAdmin)


class ReviewSellerAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title', 'created_at']


admin.site.register(ReviewSellerModel, ReviewSellerAdmin)
