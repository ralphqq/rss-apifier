import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command (BaseCommand):
    help = 'Create admin user and auth token based on env vars'

    def handle(self, *args, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel(
                username=os.environ['ADMIN_USER'],
                email=os.environ.get('ADMIN_EMAIL', ''),
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            user.set_password(os.environ['ADMIN_PASSWORD'])
            user.save()
            token = Token.objects.create(user=user)
        except Exception as e:
            self.stdout.write(f'ERROR: {e}')
        else:
            self.stdout.write(
                f'Created user {user.username} and associated API auth token'
            )
