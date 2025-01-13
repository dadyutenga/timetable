from rest_framework import serializers
from .models import (
    Department, Program, Module, Room, Staff, 
    Timetable, TeacherPreference, Class, 
    Conflict, ClassModuleAllocation
)

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'

class TeacherPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPreference
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class ConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conflict
        fields = '__all__'

class ClassModuleAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassModuleAllocation
        fields = '__all__' 