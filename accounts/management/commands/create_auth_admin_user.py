import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command (BaseCommand):
    help = 'Create admin user and auth token based on env vars'

    def handle(self, *args, **kwargs):
        username = os.environ.get('ADMIN_USER')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL')

        if username and password and email:
            UserModel = get_user_model()
            try:
                # Create super user
                user = UserModel(
                    username=username,
                    email=email,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                user.set_password(password)
                user.save()

                # Generate auth token for user
                token = Token.objects.create(user=user)
            except Exception as e:
                self.stdout.write(
                    f'Encountered an error while creating default '
                    f'admin user and generating token: {e}'
                )
            else:
                if token:
                    self.stdout.write(
                        f'Created default admin user {user.username} and '
                        f'generated API auth token'
                    )

        else:
            self.stdout.write(
                'Default auth admin user not created '
                '(1 or more credentials not found)'
            )
