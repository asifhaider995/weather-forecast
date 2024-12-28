from django.urls import path
from api.views import TestView

urlpatterns = [
    path('v1/coolest-locations', TestView.as_view()),
]