from django.contrib import admin

from store.models import BoostOrder, Coupon, Qualification, SkinsOrder


# Register your models here.

admin.site.register(Coupon)
admin.site.register(BoostOrder)
admin.site.register(Qualification)

@admin.register(SkinsOrder)
class SkinOrderAdmid(admin.ModelAdmin):
    readonly_fields = ('created_at',)
