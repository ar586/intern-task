from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KeywordViewSet, FlagViewSet, trigger_scan

router = DefaultRouter()
router.register(r'keywords', KeywordViewSet, basename='keyword')
router.register(r'flags', FlagViewSet, basename='flag')

urlpatterns = [
    path('', include(router.urls)),
    path('scan/', trigger_scan, name='trigger_scan'),
]
