from django.shortcuts import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.tests.helpers import create_entry_objects
from feeds.models import Entry


class EntryListTest(APITestCase):
    """Tests GET request on `entry-list` endpoint.

    This API call should return a JSON payload that includes 
    a paginated list of Entry objects.
    """

    @classmethod
    def setUpTestData  (cls):
        cls.endpoint_url = reverse('entry-list')

        # Create some fake entries
        cls.n_items = 275
        cls.entries = create_entry_objects(n_items=cls.n_items)

    def test_does_not_allow_post_request(self):
        response = self.client.post(self.endpoint_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_successful_get_request(self):
        response = self.client.get(self.endpoint_url)
        payload = response.json()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIsInstance(payload['results'], list)
        self.assertEqual(payload['count'], self.n_items)

    def test_valid_entries_pagination(self):
        # Pass in a page number within range
        response = self.client.get(self.endpoint_url, data={'page': 2})
        payload = response.json()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIsInstance(payload['results'], list)
        self.assertEqual(payload['count'], self.n_items)

    def test_invalid_entries_pagination(self):
        # Pass in a page number out of range
        response = self.client.get(self.endpoint_url, data={'page': 2000})
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_has_no_entries_to_fetch(self):
        # delete all entries currently in db
        Entry.objects.all().delete()
        response = self.client.get(self.endpoint_url)
        payload = response.json()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIsInstance(payload['results'], list)
        self.assertFalse(payload['results'])
        self.assertEqual(payload['count'], 0)
