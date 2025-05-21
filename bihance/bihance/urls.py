from applications.views import ApplicationsViewSet
from availabilities.views import AvailabilitiesViewSet
from companies.views import CompanyViewSet
from employer.views import EmployerViewSet
from files.views import FilesViewSet
from message.views import MessageViewSet
from reviews.views import ReviewsViewSet

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers 


router = routers.DefaultRouter()
router.register(r"applications", ApplicationsViewSet, "applications")
router.register(r"availabilities", AvailabilitiesViewSet, "availabilities")
router.register(r"companies", CompanyViewSet, "companies")
router.register(r"employer", EmployerViewSet, "employer")
router.register(r"messages", MessageViewSet, "messages")
router.register(r"reviews", ReviewsViewSet, "reviews")
router.register(r"files", FilesViewSet, "files")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]


