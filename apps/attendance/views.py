from typing import Any
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView,CreateView
from django.contrib.auth import authenticate,login,logout
from .models import *
from .forms import LeaveRequestForm
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.core.exceptions import ObjectDoesNotExist
from django.conf import Settings
import datetime , calendar
from django.views.decorators.http import require_POST

    
class EmployeeDashboard(LoginRequiredMixin,TemplateView):
    template_name = "employee_dashboard.html"
    login_url = "/login/"
    def calculate_leaves(self):
        approved_requests = LeaveRequest.objects.filter(employee=self.request.user).filter(is_approved=True)
        sick_requests = approved_requests.filter(leave_type="SICK")
        earned_requests = approved_requests.filter(leave_type="EARNED")  
        unpaid_requests = approved_requests.filter(leave_type="LOP")
        sick,unpaid,earned=0,0,0
        sick = sum([(record.end_date - record.start_date).days + 1 for record in sick_requests])
        earned = sum([(record.end_date - record.start_date).days + 1 for record in earned_requests])
        unpaid = sum([(record.end_date - record.start_date).days + 1 for record in unpaid_requests])

        return sick,earned,unpaid
    def get_context_data(self,**kwargs):
        user= self.request.user
        is_manager = user.manager.exists()
        sick,earned,unpaid = self.calculate_leaves()
        if earned>15:
            unpaid += earned - 15
            earned = 15
        else:
            earned = 15- earned
        if sick>9:
            unpaid += sick - 9
            sick = 0
        else:
            sick = 9 - sick

        leave_requests = LeaveRequest.objects.filter(employee=self.request.user).order_by("-start_date")
        context = {"form":LeaveRequestForm,"leave_requests":leave_requests,"num_requests":len(leave_requests)!=0,"employee_records":Attendance.objects.filter(employee=user).order_by("-fordate"),"is_manager":is_manager,"is_admin":user.is_superuser,"sick":sick,"earned":earned,"unpaid":abs(unpaid),"user":str(user).capitalize()}
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

    

class MarkAttendanceView(LoginRequiredMixin,TemplateView) :
    template_name = "mark_attendance.html"
    login_url = "/login/"    
    
    def get_context_data(self, **kwargs):
        members = Employee.objects.filter(manager=self.request.user)
        status = Status.objects.all()
        attendance_records = Attendance.objects.filter(employee__in=members.values('user'))
        context = {"status_options":status,"records":attendance_records,"date":datetime.datetime.strftime(datetime.datetime.today(),"%Y-%m-%d"),"employees":members,"is_manager":True,"is_admin":self.request.user.is_superuser}
        return context    
    
    def post(self,request):
        '''
        Method to post data into database
        '''
        attendance_date,records = request.POST.get("attendance_date"),json.loads(request.POST.get("records"))
        for record in records:
            remark = record['remark'] if record['remark'] != "" else str(record['status'])
            user = User.objects.get(username=record['user'])
            status = Status.objects.get(status=record['status'])
            try:
                existing_record = Attendance.objects.filter(employee=user).get(fordate=attendance_date)
                print("existing",existing_record.status)
                existing_record.status = status
                existing_record.remarks = remark
                existing_record.save()
            except ObjectDoesNotExist:
                new_record = Attendance.objects.create(employee=user,fordate=attendance_date,status=status,remarks=remark)
                new_record.save()
            # update_record,created = Attendance.objects.update_or_create(fordate=attendance_date,employee=user,status=status,remarks=remark)
            # update_record.save()
            # print("anything",update_record)
        return redirect(request.path_info)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = "/login/"

    def get_context_data(self):
        today = datetime.datetime.now()
        late_comers = []
        absent = []
        if self.request.user.is_superuser:
            total_employees = Employee.objects.all()
            p=a=s=l=0
            for employee in Attendance.objects.filter(fordate=today) :
                if str(employee.status) == "Present":
                    p += 1
                elif str(employee.status) == "Late" :
                    late_comers.append(employee)
                    l += 1
                elif str(employee.status) == "Sick":
                    s += 1
                    absent.append(employee)
                else:
                    a += 1
                    absent.append(employee)
            members = list(Employee.objects.values('user_id'))
            if not members:
                pass
            requests = []
            for i in members:
                for j in list(LeaveRequest.objects.values()) :
                    if i['user_id'] == j['employee_id'] :
                        j['name'] = str(User.objects.get(pk=j['employee_id']))
                        requests.append(j)
        else:
            total_employees = Employee.objects.filter(manager=self.request.user)
            p=a=s=l=0
            # For present day
            employees = [i for i in Attendance.objects.filter(fordate=today) if Employee.objects.get(user=i.employee).manager == self.request.user]
            for employee in employees:
                if str(employee.status) == "Present":
                    p += 1
                elif str(employee.status) == "Late" :
                    late_comers.append(employee)
                    l += 1
                elif str(employee.status) == "Sick":
                    s += 1
                    absent.append(employee)
                else:
                    a += 1
                    absent.append(employee)
            # print("b",Employee.objects.get(user=b[0].employee).manager)
            members = list(Employee.objects.filter(manager=self.request.user).values('user_id'))
            if not members:
                pass
            requests = []
            for i in members:
                for j in list(LeaveRequest.objects.values()) :
                    if i['user_id'] == j['employee_id'] :
                        j['name'] = str(User.objects.get(pk=j['employee_id']))
                        requests.append(j)
        return {"weekday":today.strftime("%A"),"date":today.strftime("%d/%m/%Y"),"requests":requests[::-1],"present":p,"abs":a,"late":l,"sick":s,"all_employees":total_employees,"late_comers":late_comers,"absent":absent,"is_manager":self.request.user.is_staff,"is_admin":self.request.user.is_superuser}


class LogoutView(TemplateView):
    def get(self,request):
        logout(request)
        return redirect("attendance:emp_dash")
    
class LeaveRequestView(LoginRequiredMixin,TemplateView):
    template_name = "leave_requests.html"
    login_url = '/login/'

    def get_context_data(self, **kwargs: Any):
        members = list(Employee.objects.filter(manager=self.request.user).values('user_id'))
        if not members:
            pass
        requests = []
        for i in members:
            for j in list(LeaveRequest.objects.values()) :
                if i['user_id'] == j['employee_id'] :
                    j['name'] = str(User.objects.get(pk=j['employee_id']))
                    requests.append(j)
        # print(requests)
        return {"data": requests[::-1]}



@require_POST
def approve_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.is_approved = True
    leave_request.save()
    return redirect("attendance:leaveRequest")


@require_POST
def reject_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.is_approved = False
    leave_request.save()
    return redirect("attendance:leaveRequest")

