from rest_framework.test import APITestCase

from feeds.api.serializers import EntrySerializer, FeedSerializer
from feeds.tests.helpers import create_and_save_feeds

# All field names of serializer output
ENTRY_DETAIL_FIELDS = EntrySerializer().Meta.fields
FEED_DETAIL_FIELDS = FeedSerializer().Meta.fields


class BaseFeedAPITestCase(APITestCase):
    """Includes methods for test cases involving Feed detail views."""

    @classmethod
    def setUpTestData(cls):
        # Create some Feed objects
        cls.n_items = 25
        cls.feeds = create_and_save_feeds(cls.n_items)

        # Get a valid PK from saved Feed objects
        cls.pk = cls.feeds.values('id')[0]['id']
