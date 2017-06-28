from django.conf.urls import url
from .views import calendar, download_schedule

urlpatterns = [
    url(r'^docx/(?P<traineeship>[0-9]+)/$', download_schedule, name="schedule"),
    url(r'^(?P<action>create|read|update|delete)/(?P<traineeship>[0-9]+)/$', calendar, name="calendar"),
]
