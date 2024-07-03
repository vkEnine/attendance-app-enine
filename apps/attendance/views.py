from typing import Any
from django.shortcuts import render,redirect
from django.views.generic import TemplateView,CreateView
from django.contrib.auth import authenticate,login,logout
from .models import *
from .forms import LeaveRequestForm
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.core.exceptions import ObjectDoesNotExist

    
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
        leave_requests = LeaveRequest.objects.filter(employee=self.request.user).order_by("-start_date")
        # print(user.)
        context = {"form":LeaveRequestForm,"leave_requests":leave_requests,"num_requests":len(leave_requests)!=0,"employee_records":Attendance.objects.filter(employee=user).order_by("-fordate"),"is_manager":is_manager,"is_admin":user.is_superuser,"sick":9-sick,"earned":15-earned,"unpaid":unpaid,"user":str(user).capitalize()}
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
    template_name = "mark_attendance.html"
    def get_context_data(self,**kwargs):
        members = Employee.objects.filter(manager=self.request.user)
        print(members)
        status = Status.objects.all()
        attendance_records = Attendance.objects.filter(employee__in=members.values('user'))
        print(attendance_records)
        context = {"status_options":status,"employees":members,"records":attendance_records,"is_manager":True,"is_admin":self.request.user.is_superuser}
        return context
    
    def post(self,request):
        '''
        Method to post data into database
        '''
        attendance_date,records = request.POST.get("attendance_date"),json.loads(request.POST.get("records"))
        for record in records:
            print(attendance_date,record)
            remark = record['remark'] if record['remark'] != "" else str(record['status'])
            print(remark)
            user = User.objects.get(username=record['user'])
            print(user,Status.objects.all())
            status = Status.objects.get(status=record['status'])
            print(status)
            try:
                existing_record = Attendance.objects.filter(employee=user).get(fordate=attendance_date)
                print("existing",existing_record.status)
                existing_record.status = status
                existing_record.remarks = remark
                existing_record.save()
            except ObjectDoesNotExist:
                new_record = Attendance.objects.create(employee=user,fordate=attendance_date,status=status,remarks=remark)
                new_record.save()
                # existing_record.save()
                # print("new",new_record)
            # update_record.save()
        return redirect(request.path_info)
    
class LeaveApplicationCreateView(CreateView):
    template_name = "leave_request_form.html"
    model = LeaveRequest
    form_class = LeaveRequestForm
    success_url = "apps.attendance:emp_dash"


class LogoutView(TemplateView):
    def get(self,request):
        logout(request)
        return redirect("attendance:emp_dash")

