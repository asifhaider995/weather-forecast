from django.urls import path
from api.views import DetermineTravel, TopCoolestView

urlpatterns = [
    path('v1/coolest-locations', TopCoolestView.as_view()),
    path('v1/determine-travel', DetermineTravel.as_view())
]