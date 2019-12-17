from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token


class CreateAuthAdminUserTest(TestCase):

    def setUp(self):
        self.UserModel = get_user_model()
        self.out = StringIO()
        self.user_env_vars = {
            'ADMIN_USER': 'admin',
            'ADMIN_PASSWORD': 'veryweakpassword',
            'ADMIN_EMAIL': 'administrator@superadmin.com'
        }

    def test_successful_create_auth_admin(self):
        username = self.user_env_vars['ADMIN_USER']
        with patch('os.environ', self.user_env_vars):
            call_command('create_auth_admin_user', stdout=self.out)

        admin_user = self.UserModel.objects.get(username=username)
        auth_token = Token.objects.get(user=admin_user)

        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)
        self.assertIsNotNone(auth_token)

    def test_command_without_env_vars(self):
        with patch('os.environ', {}):
            call_command('create_auth_admin_user', stdout=self.out)

        self.assertIn('ERROR:', self.out.getvalue())
        self.assertEqual(self.UserModel.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 0)
