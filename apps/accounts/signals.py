from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserGroup

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_group(sender, instance, created, **kwargs):
    if created:
        UserGroup.objects.create(user=instance, is_admin=instance.role == 'admin')

@receiver(post_save, sender=User)
def save_user_group(sender, instance, **kwargs):
    try:
        user_group = UserGroup.objects.get(user=instance)
        if user_group.is_admin != (instance.role == 'admin'):
            user_group.is_admin = instance.role == 'admin'
            user_group.save()
    except UserGroup.DoesNotExist:
        UserGroup.objects.create(user=instance, is_admin=instance.role == 'admin')
