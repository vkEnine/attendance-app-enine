from typing import Any
from django.shortcuts import render,redirect
from django.views.generic import TemplateView,CreateView
from django.contrib.auth import authenticate,login,logout
from .models import *
from .forms import LeaveRequestForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
# class LoginView(TemplateView):
#     template_name = "login_page.html"
#     def post(self,request):
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request,username=username,password=password)
#         print("---------------------")
#         print(user)
#         print("---------------------")
#         if user is not None:
#             form = login(request,user)
#             return redirect("attendance:emp_dash")
#         else:
#             context = {"error":"Invalid Username or Password!"}
#         return render(request,self.template_name,context)
    
class EmployeeDashboard(LoginRequiredMixin,TemplateView):
    template_name = "employee_dashboard.html"
    login_url = "/login/"
    def calculate_leaves(self):
        approved_requests = LeaveRequest.objects.filter(employee=self.request.user).filter(is_approved=True)
        sick = approved_requests.filter(leave_type="SICK").count()
        earned = approved_requests.filter(leave_type="EARNED").count()  
        unpaid = approved_requests.filter(leave_type="LOP").count()
        return sick,earned,unpaid
    def get_context_data(self,**kwargs):
        user= self.request.user
        is_manager = user.manager.exists()
        sick,earned,unpaid = self.calculate_leaves()
        leave_requests = LeaveRequest.objects.filter(employee=self.request.user)
        # print(sick,earned)
        context = {"form":LeaveRequestForm,"leave_requests":leave_requests,"num_requests":len(leave_requests)!=0,"employee_records":Attendance.objects.filter(employee=user).order_by("-fordate"),"is_manager":is_manager,"is_admin":user.is_superuser,"sick":9-sick,"earned":15-earned,"unpaid":unpaid}
        # print(context)
        return context
    def post(self,request):
        leave_type,start_date,end_date = request.POST.get("leave_type"),request.POST.get("start_date"),request.POST.get("end_date")
        new_request = LeaveRequest.objects.create(
            employee=self.request.user,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            is_approved=None
        )
        new_request.save()
        return redirect(request.path_info)
    

class ManagerDashboard(TemplateView):
    template_name = "manager.html"
    def get_context_data(self,**kwargs):
        members = Employee.objects.filter(manager=self.request.user).values('user')
        context = {"members":members,"manager_records":Attendance.objects.filter(employee__in=members)}
        return context
    
class LeaveApplicationCreateView(CreateView):
    template_name = "leave_request_form.html"
    model = LeaveRequest
    form_class = LeaveRequestForm
    success_url = "apps.attendance:emp_dash"


class LogoutView(TemplateView):
    def get(self,request):
        logout(request)
        return redirect("attendance:emp_dash")

