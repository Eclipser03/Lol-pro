from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from main.models import ReviewModel
# Register your models here.


admin.site.register(ReviewModel, DraggableMPTTAdmin)
