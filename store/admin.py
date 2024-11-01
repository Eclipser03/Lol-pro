from django.contrib import admin

from store.models import BoostOrder, Coupon, Qualification


# Register your models here.

admin.site.register(Coupon)
admin.site.register(BoostOrder)
admin.site.register(Qualification)
