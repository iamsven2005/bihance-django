from django.urls import path
from .views import ApplicationsView

# Using class-based views (CBV)
urlpatterns = [
    path("", ApplicationsView.as_view(), name="index"),
]


