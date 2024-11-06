from django.contrib import admin

from store.models import BoostOrder, Coupon, Qualification, RPorder, SkinsOrder


# Register your models here.

admin.site.register(Coupon)
admin.site.register(BoostOrder)
admin.site.register(Qualification)
admin.site.register(RPorder)

@admin.register(SkinsOrder)
class SkinOrderAdmid(admin.ModelAdmin):
    readonly_fields = ('created_at',)
