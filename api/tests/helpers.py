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


# Some helper/base classes

class BaseFeedAPITestCase(APITestCase):
    """Includes methods for test cases involving Feed detail views."""

    @classmethod
    def setUpTestData(cls):
        # Create some Feed objects
        cls.n_items = 25
        cls.feeds = create_and_save_feeds(cls.n_items)

        # Get a valid PK from saved Feed objects
        cls.pk = cls.feeds.values('id')[0]['id']
