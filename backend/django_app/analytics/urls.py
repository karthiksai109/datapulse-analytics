from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DataSourceViewSet,
    DashboardViewSet,
    WidgetViewSet,
    AnalyticsEventViewSet,
    AlertViewSet,
    ReportViewSet,
)

router = DefaultRouter()
router.register(r"sources", DataSourceViewSet, basename="datasource")
router.register(r"dashboards", DashboardViewSet, basename="dashboard")
router.register(r"widgets", WidgetViewSet, basename="widget")
router.register(r"events", AnalyticsEventViewSet, basename="event")
router.register(r"alerts", AlertViewSet, basename="alert")
router.register(r"reports", ReportViewSet, basename="report")

urlpatterns = [
    path("", include(router.urls)),
]
