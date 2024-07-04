from django.urls import path
from .views import LogoutView,EmployeeDashboard,DashboardView,LeaveRequestView,MarkAttendanceView,approve_leave,reject_leave

app_name = "attendance"

urlpatterns = [
    path('logout/',LogoutView.as_view(),name="logout"),
    path('emp/',EmployeeDashboard.as_view(),name="emp_dash"),
    path('dash/',DashboardView.as_view(),name="man_dash"),
    path("requests/", LeaveRequestView.as_view(), name="leaveRequest"),
    path("leave/<int:leave_id>/approve/",approve_leave,name="approve_leave"),
    path("leave/<int:leave_id>/reject/", reject_leave, name="reject_leave"),
    path("markattendance/",MarkAttendanceView.as_view(),name="markAttendance"),

]