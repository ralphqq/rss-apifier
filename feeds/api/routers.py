from rest_framework.routers import DefaultRouter

from feeds.api import views

router = DefaultRouter()
router.register(r'feeds', views.FeedViewSet)
