from django.urls import include, path

from feeds.api.routers import router as feed_api_router
from feeds.api import views as feed_api_views

urlpatterns = [
    path('entries/', feed_api_views.EntryList.as_view(), name='entries-list'),
    path('', include(feed_api_router.urls)),
]
