from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.contrib.auth.models import Permission, Group

@receiver(post_migrate)
def create_initial_user_groups(sender, **kwargs):
    """
    Create initial user groups after migrations
    """
    if sender.name == 'users':
        Group = apps.get_model('auth', 'Group')
        
        # Create groups
        customers_group, _ = Group.objects.get_or_create(name='Customers')
        owners_group, _ = Group.objects.get_or_create(name='Restaurant Owners')
        admin_group, created = Group.objects.get_or_create(name='Website Admins')
        
        # Assign permissions to admin group only if newly created
        if created:
            admin_permissions = Permission.objects.filter(
                content_type__app_label__in=['users', 'restaurants', 'reviews', 'menus']
            )
            admin_group.permissions.set(admin_permissions) 