from typing import Any
from django.shortcuts import render,redirect
from django.views.generic import TemplateView,CreateView
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from .models import *
from .forms import LeaveRequestForm

# Create your views here.
class LoginView(TemplateView):
    template_name = "login_page.html"
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        print("---------------------")
        print(user)
        print("---------------------")
        if user is not None:
            form = login(request,user)
            return redirect("attendance:emp_dash")
        else:
            context = {"error":"Invalid Username or Password!"}
        return render(request,self.template_name,context)
    
class EmployeeDashboard(TemplateView):
    template_name = "employee.html"
    def calculate_leaves(self):
        approved_requests = LeaveRequest.objects.filter(employee=self.request.user).filter(is_approved=True)
        sick = approved_requests.filter(leave_type="SICK").count()
        earned = approved_requests.filter(leave_type="EARNED").count()
        return sick,earned
    def get_context_data(self,**kwargs):
        user= self.request.user
        is_manager = user.manager.exists()
        sick,earned = self.calculate_leaves()
        # print(sick,earned)
        context = {"employee_records":Attendance.objects.filter(employee=user),"is_manager":is_manager,"is_admin":user.is_superuser,"sick":9-sick,"earned":15-earned}
        return context
    

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

