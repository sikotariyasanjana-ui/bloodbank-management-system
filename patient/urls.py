from django.urls import path

from django.contrib.auth.views import LoginView
from . import views
urlpatterns = [
    path('patient-login/', LoginView.as_view(template_name='patient/login.html'),name='patient-login'),
    path('patient-signup/', views.patient_signup_view,name='patient-signup'),
    path('patient-dashboard/', views.patient_dashboard_view,name='patient-dashboard'),
    path('make-request/', views.make_request_view,name='make-request'),
    path('my-request/', views.my_request_view,name='my-request'),
]