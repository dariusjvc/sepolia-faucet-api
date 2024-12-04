from django.urls import path
from .views import fund_view, stats_view

urlpatterns = [
    path('fund/', fund_view),  # Endpoint to ask funds
    path('stats/', stats_view),  # Endpoint to aks the stats
]
