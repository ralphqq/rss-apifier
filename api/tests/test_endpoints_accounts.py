from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class ObtainAuthTokenTest(APITestCase):
    """Tests API calls on the `obtain-auth-token` endpoint.

    Valid requests should return a JSON payload with the token 
    associated with a given user.
    """

    def setUp(self):
        self.endpoint_url = reverse('obtain-auth-token')
        self.UserModel = get_user_model()

        # User credentials
        self.user_credentials = [
            {'username': 'user1', 'password': '12345678'},
            {'username': 'user2', 'password': '87654321'},
        ]

        # Create admin user with auth token
        self.user1 = self.UserModel(
            username=self.user_credentials[0]['username'],
            is_staff=True
        )
        self.user1.set_password(self.user_credentials[0]['password'])
        self.user1.save()
        self.token1 = Token.objects.create(user=self.user1)

        # Create user without token
        self.user2 = self.UserModel(
            username=self.user_credentials[1]['username'],
            is_staff=True
        )
        self.user2.set_password(self.user_credentials[1]['password'])
        self.user2.save()

    def test_auth_user_obtains_token(self):
        response = self.client.post(
            self.endpoint_url,
            data=self.user_credentials[0]
        )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload['token'], self.token1.key)

    def test_user_with_no_token_tries_to_obtain_one(self):
        response = self.client.post(
            self.endpoint_url,
            data=self.user_credentials[1]
        )
        payload = response.json()
        token2 = Token.objects.get(user=self.user2)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(payload['token'])
        self.assertEqual(payload['token'], token2.key)

    def test_request_sends_wrong_credentials(self):
        response = self.client.post(
            self.endpoint_url,
            data={
                'username': self.user_credentials[0]['username'],
                'password': self.user_credentials[1]['password']
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_make_get_request_on_endpoint(self):
        response = self.client.get(self.endpoint_url)
        self.assertEqual(response.status_code, 405)
