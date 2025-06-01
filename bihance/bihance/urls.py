from applications.views import ApplicationsViewSet
from availabilities.views import AvailabilitiesViewSet
from companies.views import CompanyViewSet
from django.contrib import admin
from django.urls import include, path
from employer.views import EmployerViewSet
from files.views import FilesViewSet
from jobs.views import JobsViewSet
from message.views import MessageViewSet
from rest_framework import routers
from reviews.views import ReviewsViewSet
from suggestions.views import SuggestionsViewSet
from users.views import UsersViewSet

router = routers.DefaultRouter()
router.register(r"applications", ApplicationsViewSet, "applications")
router.register(r"availabilities", AvailabilitiesViewSet, "availabilities")
router.register(r"companies", CompanyViewSet, "companies")
router.register(r"employer", EmployerViewSet, "employer")
router.register(r"files", FilesViewSet, "files")
router.register(r"jobs", JobsViewSet, "jobs")
router.register(r"messages", MessageViewSet, "messages")
router.register(r"reviews", ReviewsViewSet, "reviews")
router.register(r"suggestions", SuggestionsViewSet, "suggestions")
router.register(r"users", UsersViewSet, "users")


urlpatterns = [path("admin/", admin.site.urls), path("api/", include(router.urls))]
