from django.urls import path
from .views import LogoutView,EmployeeDashboard,ManagerDashboard,LeaveApplicationCreateView

app_name = "attendance"

urlpatterns = [
    path('logout/',LogoutView.as_view(),name="logout"),
    path('emp/',EmployeeDashboard.as_view(),name="emp_dash"),
    path('man/',ManagerDashboard.as_view(),name="man_dash"),
    path('requestleave/',LeaveApplicationCreateView.as_view(),name="request_leave"),
]