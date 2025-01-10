from django import forms
from .models import Module, Department, Room, Staff , Program

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = [
            'module_code',
            'module_name',
            'module_type',
            'module_year',
            'semester',
            'nta_level',
            'module_credit'
        ]

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dept_name', 'dept_descr', 'hod', 'hod_phone', 'hod_email']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_name', 'room_description', 'room_type', 'capacity', 'building_name', 'room_no']

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_name', 'rfid_id', 'staff_email', 'staff_phone', 'staff_type', 'staff_title', 'dept_id']


class ProgramForm(forms.ModelForm):
    dept_id = forms.ModelChoiceField(queryset=Department.objects.all(), label="Department")

    class Meta:
        model = Program
        fields = ['program_name', 'dept_id', 'nta_level']
        labels = {
            'program_name': 'Program Name',
            'nta_level': 'NTA Level'
        }