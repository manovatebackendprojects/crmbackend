from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, ActivityViewSet, AISuggestionViewSet, MarketingPerformanceViewSet

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'suggestions', AISuggestionViewSet, basename='suggestion')
router.register(r'performance', MarketingPerformanceViewSet, basename='performance')

urlpatterns = [
    path('', include(router.urls)),
]