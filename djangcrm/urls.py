from django.contrib import admin
from django.urls import path, include
from leads.views import LandingPage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('leads/', include('leads.urls', namespace="leads")),
    path('', LandingPage.as_view(), name='landing-page'),
]
