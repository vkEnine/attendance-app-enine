from django.forms import ModelForm,DateInput
from .models import LeaveRequest

class LeaveRequestForm(ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["employee","leave_type","start_date","end_date"]
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'})
        }