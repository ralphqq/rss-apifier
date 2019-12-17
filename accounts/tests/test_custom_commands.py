from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from rest_framework.authtoken.models import Token


class CreateAuthAdminUserTest(TestCase):
    """Tests `create_auth_admin_user` custom command."""

    def setUp(self):
        self.out = StringIO()
        self.UserModel = get_user_model()
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

    @patch(
        'accounts.management.commands.create_auth_admin_user.get_user_model'
    )
    def test_command_without_env_vars(self, mock_get_user):
        with patch('os.environ', {}):
            call_command('create_auth_admin_user', stdout=self.out)

        self.assertFalse(mock_get_user.called)
        self.assertIn(
            'Default auth admin user not created',
            self.out.getvalue()
        )
        self.assertEqual(self.UserModel.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 0)

    @patch.object(Token.objects, 'create', return_value=None)
    def test_errors_while_generating_token(self, mock_generate):
        username = self.user_env_vars['ADMIN_USER']
        with patch('os.environ', self.user_env_vars):
            mock_generate.side_effect = ValueError
            call_command('create_auth_admin_user', stdout=self.out)

        admin_user = self.UserModel.objects.get(username=username)

        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)
        self.assertIn('Encountered an error', self.out.getvalue())
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=admin_user)
