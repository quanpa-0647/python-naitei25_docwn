from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from accounts.models import User
from constants import UserRole

class Command(BaseCommand):
    help = _('Setup Django Groups và Permissions')

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help=_('Reset tất cả groups và permissions'),
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.reset_groups()

        self.create_groups_and_permissions()
        self.assign_existing_users()

        self.stdout.write(
            self.style.SUCCESS(_('Successfully setup groups and permissions!'))
        )

    def reset_groups(self):
        """Reset tất cả groups"""
        self.stdout.write(_('Resetting groups...'))
        Group.objects.all().delete()

    def create_groups_and_permissions(self):
        """Tạo groups và gán permissions"""

        # === SYSTEM ADMINS GROUP ===
        system_admin_group, created = Group.objects.get_or_create(name=UserRole.SYSTEM_ADMIN.name)
        if created:
            self.stdout.write(_('Created System Admins group'))

        all_permissions = Permission.objects.all()
        system_admin_group.permissions.set(all_permissions)

        # === WEBSITE ADMINS GROUP ===
        website_admin_group, created = Group.objects.get_or_create(name=UserRole.WEBSITE_ADMIN.name)
        if created:
            self.stdout.write(_('Created Website Admins group'))

        admin_permissions = Permission.objects.filter(
            codename__in=[
                # Content management - novels, chapters, etc
                'view_novel', 'add_novel', 'change_novel', 'delete_novel',
                'view_chapter', 'add_chapter', 'change_chapter', 'delete_chapter',
                'view_volume', 'add_volume', 'change_volume', 'delete_volume',
                'view_chunk', 'add_chunk', 'change_chunk', 'delete_chunk',

                # Authors and Artists management
                'view_author', 'add_author', 'change_author', 'delete_author',
                'view_artist', 'add_artist', 'change_artist', 'delete_artist',

                # Tags management
                'view_tag', 'add_tag', 'change_tag', 'delete_tag',
                'view_noveltag', 'add_noveltag', 'change_noveltag', 'delete_noveltag',

                # Comments và Reviews moderation
                'view_comment', 'change_comment', 'delete_comment',
                'view_review', 'change_review', 'delete_review',

                # Reports handling
                'view_report', 'change_report', 'delete_report',

                # Notifications management
                'view_notification', 'add_notification', 'change_notification', 'delete_notification',

                # User activities (có thể xem để moderate)
                'view_favorite', 'view_readinghistory',
            ]
        )
        website_admin_group.permissions.set(admin_permissions)

        # === REGULAR USERS GROUP ===
        user_group, created = Group.objects.get_or_create(name=UserRole.USER.name)
        if created:
            self.stdout.write(_('Created Regular Users group'))

        user_permissions = Permission.objects.filter(
            codename__in=[
                # Xem content
                'view_novel', 'view_chapter', 'view_volume', 'view_chunk',
                'view_author', 'view_artist', 'view_tag',

                # Tương tác với content
                'add_comment', 'view_comment',
                'add_review', 'view_review',
                'add_favorite', 'view_favorite', 'change_favorite', 'delete_favorite',
                'add_readinghistory', 'view_readinghistory', 'change_readinghistory',

                # Profile management
                'view_userprofile', 'change_userprofile',

                # Notifications
                'view_notification', 'change_notification',

                # Report content
                'add_report', 'view_report',
            ]
        )
        user_group.permissions.set(user_permissions)

        # === GUESTS GROUP ===
        guest_group, created = Group.objects.get_or_create(name=UserRole.GUEST.name)
        if created:
            self.stdout.write(_('Created Guests group'))

        guest_permissions = Permission.objects.filter(
            codename__in=[
                # Chỉ xem content cơ bản
                'view_novel', 'view_chapter', 'view_volume', 'view_chunk',
                'view_author', 'view_artist', 'view_tag',
                'view_comment', 'view_review',
            ]
        )
        guest_group.permissions.set(guest_permissions)

    def assign_existing_users(self):
        """Gán existing users vào groups theo role"""

        # System Admins
        system_admins = User.objects.filter(role=UserRole.SYSTEM_ADMIN.value)
        system_admin_group = Group.objects.get(name='System Admins')
        for user in system_admins:
            user.groups.clear()
            user.groups.add(system_admin_group)
            self.stdout.write(_('Added %(email)s to System Admins') % {'email': user.email})

        # Website Admins
        website_admins = User.objects.filter(role=UserRole.WEBSITE_ADMIN.value)
        website_admin_group = Group.objects.get(name='Website Admins')
        for user in website_admins:
            user.groups.clear()
            user.groups.add(website_admin_group)
            self.stdout.write(_('Added %(email)s to Website Admins') % {'email': user.email})

        # Regular Users
        regular_users = User.objects.filter(role=UserRole.USER.value)
        user_group = Group.objects.get(name='Regular Users')
        for user in regular_users:
            user.groups.clear()
            user.groups.add(user_group)
            self.stdout.write(_('Added %(email)s to Regular Users') % {'email': user.email})

        # Guests
        guests = User.objects.filter(role=UserRole.GUEST.value)
        guest_group = Group.objects.get(name='Guests')
        for user in guests:
            user.groups.clear()
            user.groups.add(guest_group)
            self.stdout.write(_('Added %(email)s to Guests') % {'email': user.email})
