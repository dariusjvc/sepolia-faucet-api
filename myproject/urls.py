from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from myapi.views import fund_view, stats_view 


schema_view = get_schema_view(
    openapi.Info(
        title="Company Faucet API",
        default_version='v1',
        description=(
            "It enables users to securely request Sepolia ETH from the faucet. "
            "Designed for efficient transactions, it features robust error handling "
            "and configurable rate limits to enhance user experience."
        ),
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="dario.val.cast@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('faucet/fund/', fund_view, name='fund'),
    path('faucet/stats/', stats_view, name='stats'),
    path('api/docs/v1/company', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
