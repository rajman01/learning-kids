from django.contrib import admin
from .models import Category, Video, Image


class VideoAdmin(admin.StackedInline):
    model = Video
    extra = 1


class ImageAdmin(admin.StackedInline):
    model = Image
    extra = 1


@admin.register(Category)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [VideoAdmin, ImageAdmin]

    class Meta:
        model = Category


admin.register(Video, VideoAdmin)
admin.register(Image, ImageAdmin)
