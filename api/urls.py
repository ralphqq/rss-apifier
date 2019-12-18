from django.urls import include, path
from rest_framework.authtoken import views

from feeds.api.routers import router as feed_api_router

urlpatterns = [
    path('', include(feed_api_router.urls)),
    path('accounts/token/', views.obtain_auth_token, name='obtain-auth-token'),
]
