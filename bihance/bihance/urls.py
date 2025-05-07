from applications.views import ApplicationsViewSet
from availabilities.views import AvailabilitiesViewSet
from companies.views import CompanyViewSet
from message.views import MessageViewSet
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers 


router = routers.DefaultRouter()
router.register(r"applications", ApplicationsViewSet)
router.register(r"availabilities", AvailabilitiesViewSet)
router.register(r"messages", MessageViewSet)
router.register(r"companies", CompanyViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
