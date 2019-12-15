from unittest.mock import patch

from django.shortcuts import reverse

from api.tests.helpers import (
    BaseFeedAPITestCase, create_entry_objects, FEED_DETAIL_FIELDS
)
from feeds.models import Feed


class FeedListTest(BaseFeedAPITestCase):
    """Tests GET request on `feed-list` endpoint.

    This API call should return a JSON payload that includes 
    a paginated list of Feed objects.
    """

    def setUp(self):
        self.create_and_authenticate_user('testadmin')
        self.endpoint_url = reverse('feed-list')

    def test_successful_get_request(self):
        response = self.client.get(self.endpoint_url)
        payload = response.json()
        self.assert_http_status(response)
        self.assertIsInstance(payload['results'], list)
        self.assertEqual(payload['count'], self.n_items)

    def test_has_no_feeds_to_fetch(self):
        # delete all entries currently in db
        Feed.objects.all().delete()
        response = self.client.get(self.endpoint_url)
        payload = response.json()
        self.assert_http_status(response)
        self.assertIsInstance(payload['results'], list)
        self.assertEqual(payload['count'], 0)


class FeedDetailTest(BaseFeedAPITestCase):
    """Tests GET request on `feed-detail` endpoint.

    This API call should retrieve a single Feed object.
    """

    def setUp(self):
        self.create_and_authenticate_user('testadmin')

    def test_successful_retrieval(self):
        url = reverse('feed-detail', kwargs={'pk': self.pk})
        response = self.client.get(url)
        payload = response.json()
        self.assert_http_status(response)
        self.assertIsInstance(payload, dict)
        self.assertCountEqual(payload.keys(), FEED_DETAIL_FIELDS)

    def test_retrieving_nonexistent_feed(self):
        url = reverse('feed-detail', kwargs={'pk': 100})
        response = self.client.get(url)
        self.assert_http_status(response, 404)


@patch('feeds.api.views.Feed.fetch_and_set_feed_details')
class CreateFeedTest(BaseFeedAPITestCase):
    """Tests POST request on `feed-list` endpoint.

    This API call should create a new Feed object.
    """

    def setUp(self):
        self.create_and_authenticate_user('testadmin')
        self.endpoint_url = reverse('feed-list')

    def test_successful_feed_creation(self, mock_fetch):
        valid_payload = {
            'link': 'https://www.feeds-me-up.com/',
            'title': 'Title 1',
            'description': 'Description',
            'version': 'rss20'
        }
        response = self.client.post(
            self.endpoint_url,
            data=valid_payload,
            format='json'
        )
        self.assert_http_status(response, 201)
        self.assertTrue(mock_fetch.called)

    def test_feed_creation_with_link_only(self, mock_fetch):
        valid_payload = {'link': 'https://www.feeds-me-up-x.com/'}
        response = self.client.post(
            self.endpoint_url,
            data=valid_payload,
            format='json'
        )
        self.assert_http_status(response, 201)
        self.assertTrue(mock_fetch.called)

    def test_invalid_feed_creation_request(self, mock_fetch):
        invalid_payload = {'link': 'invalid'}
        response = self.client.post(
            self.endpoint_url,
            data=invalid_payload,
            format='json'
        )
        self.assert_http_status(response, 400)
        self.assertFalse(mock_fetch.called)


@patch('feeds.api.views.Feed.fetch_and_set_feed_details')
class UpdateFeedTest(BaseFeedAPITestCase):
    """Tests PUT requests on `feed-detail` endpoint.

    This API call should update a given Feed object.
    """

    def setUp(self):
        self.create_and_authenticate_user('testadmin')
        self.feed = Feed.objects.get(pk=self.pk)
        self.valid_payload = {'link': self.feed.link}
        self.endpoint_url = reverse('feed-detail', kwargs={'pk': self.pk})

    def test_valid_update(self, mock_fetch):
        self.valid_payload['title'] = 'New Title'
        self.valid_payload['description'] = 'New description'
        response = self.client.put(
            self.endpoint_url,
            data=self.valid_payload,
            format='json'
        )
        self.assert_http_status(response)

    def test_invalid_update(self, mock_fetch):
        invalid_payload = {'notvalid': 'notvalid'}
        response = self.client.put(
            self.endpoint_url,
            data=invalid_payload,
            format='json'
        )
        self.assert_http_status(response, 400)


class DeleteFeedTest(BaseFeedAPITestCase):
    """Tests DELETE requests on `feed-detail` endpoint.

    This API call should delete a given Feed object.
    """

    def setUp(self):
        self.create_and_authenticate_user('testadmin')
        self.feed = Feed.objects.get(pk=self.pk)
        self.endpoint_url = reverse('feed-detail', kwargs={'pk': self.pk})

    def test_successful_delete(self):
        response = self.client.delete(self.endpoint_url)
        self.assert_http_status(response, 204)
        with self.assertRaises(Feed.DoesNotExist):
            Feed.objects.get(pk=self.pk)


class FeedEntriesListTest(BaseFeedAPITestCase):
    """Tests GET requests on `feed-entries` endpoint.

    This API call should return a JSON payload that includes a list of 
    Entry objects associated with a given Feed object.
    """

    def setUp(self):
        self.create_and_authenticate_user('testadmin')
        self.endpoint_url = reverse('feed-entries', kwargs={'pk': self.pk})
        self.feed = Feed.objects.get(pk=self.pk)

    def test_valid_feed_entries_retrieval(self):
        # Create some Entry objects and associate with a Feed
        n_entries = 120
        feed_url = self.feed.link
        entries = create_entry_objects(n_entries, feed_url)
        for entry in entries:
            self.feed.entries.add(entry)

        # Fetch this feed's entries via API endpoint
        response = self.client.get(self.endpoint_url)
        payload = response.json()
        self.assert_http_status(response)
        self.assertIsInstance(payload['results'], list)
        self.assertEqual(payload['count'], self.feed.entries.count())
