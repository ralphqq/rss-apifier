from django.urls import path

from feeds.api import views as feed_api_views

urlpatterns = [
    path('entries/', feed_api_views.EntryList.as_view(), name='entries-list'),
    path('feeds/', feed_api_views.FeedList.as_view(), name='feeds-list'),
    path(
        'feeds/<int:pk>',
        feed_api_views.FeedDetail.as_view(),
        name='feed-details'
    ),
    path(
        'feeds/<int:pk>/entries/',
        feed_api_views.FeedEntryList.as_view(),
        name='feed-entries-list'
    ),
]
