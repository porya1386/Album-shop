from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf.urls.i18n import i18n_patterns
from django.urls import re_path
from django.views.static import serve

# ---- Swagger ----
schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    # url-e set_language                      # API ha bedoone prefix
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("accounts/", include("accounts.urls")),
    path("", include("website.urls")),
    path("shop/", include("shop.urls")),
    path("admin/", admin.site.urls),
    path("comments/", include("reviews.urls")),
    # prefix_default_language=False   <-- hazf kon (pishfarz True hast)
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
# Swagger
urlpatterns += [
    path("swagger.<format>/",
         schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger",
         cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc",
         cache_timeout=0), name="schema-redoc"),
]

if not settings.DEBUG and not getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""):
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve,
                {"document_root": settings.MEDIA_ROOT}),
    ]
