from django.db import models

from feeds.utils.feed_tools import fetch_feedparser_dict


class Feed(models.Model):
    title = models.CharField(max_length=1024)
    description = models.CharField(max_length=2048, default='')
    link = models.URLField(max_length=400, null=False, unique=True)
    version = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        """Fetches details about feed and saves it."""
        if not self.link:
            raise TypeError('No URL for feed provided')
        feed = fetch_feedparser_dict(feed_url=self.link)
        self.title = feed.get('title', '')
        self.description = feed.get('description', '')
        self.version = feed.get('version', '')
        super().save(*args, **kwargs)
