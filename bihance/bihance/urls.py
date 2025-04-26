from applications import views
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers 

router = routers.DefaultRouter()
router.register(r"applications", views.ApplicationsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
