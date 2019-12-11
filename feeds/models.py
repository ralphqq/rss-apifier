from django.conf import settings
from django.db import IntegrityError, models
from django.utils import timezone

from feeds.utils.feed_tools import (
    fetch_feedparser_dict, preprocess_feed_entry_item
)


class Entry(models.Model):
    link = models.URLField(max_length=800, unique=True)
    published = models.DateTimeField(default=timezone.now)
    summary = models.TextField()
    title = models.CharField(max_length=280)
    timestamp = models.DateTimeField(default=timezone.now)
    feeds = models.ManyToManyField('Feed', related_name='entries')

    class Meta:
        indexes = [
            models.Index(fields=['link']),
            models.Index(fields=['published']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-published']

    def __str__(self):
        return self.title


class Feed(models.Model):
    title = models.CharField(max_length=1024)
    description = models.CharField(max_length=2048, default='')
    link = models.URLField(max_length=400, null=False, unique=True)
    version = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        """Overrides the built-in save method.

        For new Feed objects, this method fetches meta data 
        about the feed and includes these when saving. For existing 
        Feed objects, the method behaves as the original save method.

        Raises:
            TypeError: when the Feed link is not given
        """
        if not self.link:
            raise TypeError('No URL for feed provided')

        try:
            feed = Feed.objects.get(link=self.link)
        except Feed.DoesNotExist: 
            self.fetch_and_set_feed_details()
        super().save(*args, **kwargs)

    def fetch_and_set_feed_details(self):
        """Fetches meta details about feed from its URL.

        The fetched values ar then assigned to 
        the appropriate fields of the Feed model. 
        Note that the method does not call save().

        Raises:
            TypeError: when the Feed link is not given
        """
        if not self.link:
            raise TypeError('No URL for feed provided')

        parsed_feed = fetch_feedparser_dict(feed_url=self.link)
        self.title = parsed_feed.feed.get('title', '')
        self.description = parsed_feed.feed.get('description', '')
        self.version = parsed_feed.get('version', '')

    def update_feed_entries(self):
        """Fetches a given feed's available entries.

        The method then tries to save all new entries.

        Returns:
            int: count of successfully saved entries
        """
        parsed_feed = fetch_feedparser_dict(self.link)
        saved_entries_count = 0
        old_entries_count = 0
        for feed_entry in parsed_feed.entries:
            # Check if max count is reached
            if old_entries_count >= settings.MAX_SAVED_ENTRIES_COUNT:
                break

            try:
                # Process raw entry and 
                # create Entry object if it does not exist yet
                item = preprocess_feed_entry_item(feed_entry)
                entry, _ = Entry.objects.get_or_create(
                    link=item['link'],
                    defaults={k: v for k, v in item.items() if k != 'link'}
                )

                # Check existing entry is already part of current feed
                old_entry = self.entries.filter(link=entry.link)

                if old_entry.exists():
                    old_entries_count += 1
                    continue
                else:
                    self.entries.add(entry)

            except Exception as e:
                pass
            else:
                saved_entries_count += 1
                old_entries_count = 0

        return saved_entries_count
