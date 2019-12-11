from rest_framework import generics

from feeds.api.serializers import EntrySerializer, FeedSerializer
from feeds.models import Entry, Feed


class EntryList(generics.ListAPIView):
    """Lists all saved entries."""
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer


class FeedList(generics.ListAPIView):
    """Lists all registered RSS feeds."""
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer


class FeedDetail(generics.RetrieveAPIView):
    """Gives details of a single RSS feed."""
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer


class FeedEntryList(generics.ListAPIView):
    """Lists all entries associated with a given RSS feed."""
    serializer_class = EntrySerializer

    def get_queryset(self):
        """Overrides `get_queryset()` to get only this feed's entries."""
        feed_pk = self.kwargs.get('pk')
        if feed_pk is None:
            raise TypeError('Primary key not found in URL')
        feed = Feed.objects.get(pk=feed_pk)
        return feed.entries.all()
