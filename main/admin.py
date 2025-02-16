from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from main.models import ReviewModel


class ReviewAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title', 'created_at']


admin.site.register(ReviewModel, ReviewAdmin)
