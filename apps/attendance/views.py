from typing import Any
from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from .models import *

# Create your views here.
class LoginView(TemplateView):
    template_name = "login_page.html"
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            form = login(request,user)
            return redirect("attendance:emp_dash")
        return HttpResponse("Login Failed")
    
class EmployeeDashboard(TemplateView):
    template_name = "employee.html"
    def get_context_data(self,**kwargs):
        user= self.request.user
        is_manager = user.manager.exists()
        context = {"employee_records":Attendance.objects.filter(employee=user),"is_manager":is_manager,"is_admin":user.is_superuser}
        return context
    

class ManagerDashboard(TemplateView):
    template_name = "manager.html"
    def get_context_data(self,**kwargs):
        members = Employee.objects.filter(manager=self.request.user).values('user')
        context = {"members":members,"manager_records":Attendance.objects.filter(employee__in=members)}
        return context
    
