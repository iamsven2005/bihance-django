from applications.views import ApplicationsViewSet
from availabilities.views import AvailabilitiesViewSet
from companies.views import CompanyViewSet
from employer.views import EmployerViewSet
from message.views import MessageViewSet
from reviews.views import ReviewsViewSet

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers 


router = routers.DefaultRouter()
router.register(r"applications", ApplicationsViewSet)
router.register(r"availabilities", AvailabilitiesViewSet)
router.register(r"messages", MessageViewSet)
router.register(r"companies", CompanyViewSet)
router.register(r"employer", EmployerViewSet)
router.register(r"reviews", ReviewsViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
