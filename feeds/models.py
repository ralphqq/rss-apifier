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
            parsed_feed = fetch_feedparser_dict(feed_url=self.link)
            self.title = parsed_feed.feed.get('title', '')
            self.description = parsed_feed.feed.get('description', '')
            self.version = parsed_feed.get('version', '')

        super().save(*args, **kwargs)
