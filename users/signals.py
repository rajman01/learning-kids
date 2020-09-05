from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import ParentProfile


@receiver(post_save, sender=User)
def create_parentprofile(sender, instance,  created, **kwargs):
    if created:
        ParentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_parentprofile(sender, instance, **kwargs):
    instance.parentprofile.save()
