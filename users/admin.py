from django.contrib import admin
from .models import ParentProfile, ChildrenProfile


class ChildrenProfileAdmin(admin.StackedInline):
    model = ChildrenProfile
    extra = 1


@admin.register(ParentProfile)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ChildrenProfileAdmin]

    class Meta:
        model = ParentProfile


admin.register(ChildrenProfile, ChildrenProfileAdmin)