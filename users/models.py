from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

User._meta.get_field('email')._unique = True


class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatar', blank=True, null=True, default='default.jpg')
    objects = models.Manager()

    def __str__(self):
        return f'{self.user.username} Profile'


class ChildrenProfile(models.Model):
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    age = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    GENDER_CHOICES = (
        ('Female', 'Female'),
        ('Male', 'Male'),
    )
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, default='Male')
    avatar = models.ImageField(upload_to='avatar', blank=True, null=True, default='child_default.png')
    objects = models.Manager()

    class Meta:
        unique_together = (("parent", "name"),)

    def __str__(self):
        return f'{self.name} child of {self.parent.user.username}'

