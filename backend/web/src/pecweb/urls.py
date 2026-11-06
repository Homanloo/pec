from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from pecweb import views

api = [
    path("health/", views.health),
    path("models/", views.models),
    path("components/", views.components),
    path("components/<str:name>/", views.component),
    path("flash/", views.flash),
    path("saturation-point/", views.saturation_point),
    path("envelope/", views.envelope),
    path("binary/", views.binary),
    path("pure/curve/", views.pure_curve),
    path("pure/isotherms/", views.isotherms),
]

urlpatterns = [
    path("api/v1/", include(api)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # Everything else is a page of the frontend (it routes in the browser)
    re_path(r"^(?!api/|static/).*$", views.spa),
]
