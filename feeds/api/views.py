from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from feeds.api.serializers import EntrySerializer, FeedSerializer
from feeds.models import Entry, Feed


class EntryList(generics.ListAPIView):
    """Lists all saved entries."""
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer


class FeedViewSet(viewsets.ModelViewSet):
    """Handles list, detail, and custom view methods for Feed."""
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer

    @action(detail=True, url_name='entries')
    def entries(self, *args, **kwargs):
        """Lists all entries associated with a given RSS feed."""
        feed = self.get_object()
        serializer = EntrySerializer(feed.entries.all(), many=True)
        return Response(serializer.data)
