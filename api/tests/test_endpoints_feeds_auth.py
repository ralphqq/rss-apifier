from unittest.mock import patch

from django.shortcuts import reverse
from rest_framework import status

from api.tests.helpers import (
    BaseFeedAPITestCase, create_user_and_auth_token
)


class BaseFeedAuthTestCase(BaseFeedAPITestCase):
    """Tests read/write Feed endpoints for admin with valid token.

    These API calls should return a 200 ok status, or a 
    201 created status, depending on the request.
    """

    def setUp(self):
        # Create some auth credentials
        self.user, self.token = create_user_and_auth_token(
            username='admin',
            is_staff=True
        )

        # Include an appropriate `Authorization:` header on all requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Set user as current user
        self.client.request(user=self.user)

        # Set expected status code per test
        self.listing_test_code = status.HTTP_200_OK
        self.creation_test_code = status.HTTP_201_CREATED

    def test_retrieving_all_feeds(self):
        response = self.client.get(reverse('feed-list'))
        self.assert_http_status(response, self.listing_test_code)

    @patch('feeds.api.views.Feed.fetch_and_set_feed_details')
    def test_creating_a_new_feed(self, mock_fetch):
        response = self.client.post(
            reverse('feed-list'),
            data={'link': 'https://www.feeds-me-up-x.com/'},
            format='json'
        )
        self.assert_http_status(response, self.creation_test_code)


class FeedViewWithInvalidToken(BaseFeedAuthTestCase):
    """Read/Write Feed endpoints for admin without valid token.

    These API calls should return a 401 unauthorized error.
    """

    def setUp(self):
        super().setUp()

        # Remove credentials
        self.client.credentials()

        # Set expected status codes for each test
        self.listing_test_code = status.HTTP_401_UNAUTHORIZED
        self.creation_test_code = status.HTTP_401_UNAUTHORIZED


class FeedViewsWithNonAdminUser(BaseFeedAuthTestCase):
    """Read/Write Feed endpoints for non-admin with valid token.

    These API calls should return a 403 forbidden error.
    """

    def setUp(self):
        super().setUp()

        # Change user privilege
        self.user.is_staff = False
        self.user.save()

        # Set expected HTTP status codes for each test
        self.listing_test_code = status.HTTP_403_FORBIDDEN
        self.creation_test_code = status.HTTP_403_FORBIDDEN
