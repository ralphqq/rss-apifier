from django.urls import include, path

from feeds.api.routers import router as feed_api_router

urlpatterns = [
    path('', include(feed_api_router.urls)),
]
