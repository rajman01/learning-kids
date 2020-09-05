from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=240, unique=True)
    description = models.TextField(null=True, blank=True)
    objects = models.Manager()


class Image(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=240, blank=True, null=True)
    image_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='uploads')
    objects = models.Manager()


class Video(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=240, blank=True, null=True)
    video_description = models.TextField(blank=True, null=True)
    video_link = models.URLField(max_length=300)
    objects = models.Manager()

