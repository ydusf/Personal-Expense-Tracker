from django.db.models.signals import post_save, post_delete
from .models import CustomUser, Profile, GeneralBudget
from django.dispatch import receiver
import os

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        GeneralBudget.objects.create(user=instance)
    instance.profile.save()
    instance.generalbudget.save()

@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.image and instance.image.name != 'default_profile.png':
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)