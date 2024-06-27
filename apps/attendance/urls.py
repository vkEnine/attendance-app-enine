from django.urls import path
from .views import LoginView,EmployeeDashboard,ManagerDashboard

app_name = "attendance"

urlpatterns = [
    path('login/',LoginView.as_view(),name="login"),
    path('emp/',EmployeeDashboard.as_view(),name="emp_dash"),
    path('man/',ManagerDashboard.as_view(),name="man_dash"),
]