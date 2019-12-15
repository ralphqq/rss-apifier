from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from feeds.api.serializers import EntrySerializer, FeedSerializer
from feeds.models import Entry
from feeds.tests.helpers import (
    create_and_save_feeds,
    make_preprocessed_entries_list
)

# Some helper constants

ENTRY_DETAIL_FIELDS = EntrySerializer().Meta.fields
FEED_DETAIL_FIELDS = FeedSerializer().Meta.fields


# Some helper functions

def create_entry_objects(n_items=100, feed_url='https://www.myfeed.com/'):
    """Convenience function to create Entry objects in bulk."""
    return Entry.objects.bulk_create([
        Entry(**data) for data in make_preprocessed_entries_list(
            n_items=n_items,
            feed_url=feed_url
        )
    ])


def create_user_and_auth_token(username, is_staff=False):
    """Creates a user and generates token for the user.

    Returns:
        tuple: (User object, token)
    """
    user = User.objects.create(
        username=username,
        email=f'{username}@rssapifier.com',
        is_staff=is_staff
    )
    token = Token.objects.create(user=user)
    return user, token


# Some helper/base classes

class BaseRSSAPITestCase(APITestCase):
    """Includes methods common to all test cases in this project."""

    def assert_http_status(self, response, expected_status_code=200):
        """Asserts if response status code is exactly as expected."""
        self.assertEqual(
            response.status_code,
            expected_status_code
        )


class BaseFeedAPITestCase(BaseRSSAPITestCase):
    """Includes methods for test cases involving Feed list/detail."""

    @classmethod
    def setUpTestData(cls):
        # Create some Feed objects
        cls.n_items = 25
        cls.feeds = create_and_save_feeds(cls.n_items)

        # Get a valid PK from saved Feed objects
        cls.pk = cls.feeds.values('id')[0]['id']

    def create_and_authenticate_user(self, username='', is_staff=True):
        """Convenience method for user creation and auth."""
        user, token = create_user_and_auth_token(
            username=username,
            is_staff=is_staff
        )
        self.client.force_authenticate(user=user, token=token)
