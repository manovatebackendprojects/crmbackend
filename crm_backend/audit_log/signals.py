from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog


def create_audit_log(instance, action, user=None, changes=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        changes=changes
    )


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender.__name__ == 'AuditLog':
        return

    action = 'CREATE' if created else 'UPDATE'
    create_audit_log(instance, action)


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender.__name__ == 'AuditLog':
        return

    create_audit_log(instance, 'DELETE')
