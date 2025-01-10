from rest_framework import serializers
from .models import (
    Module,
    Department,
    Room,
    Staff,
    Program,
    Class,
    ClassModuleAllocation,
    Timetable,
    TeacherPreference,
    Conflict
)

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class ClassModuleAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassModuleAllocation
        fields = '__all__'

class TimetableSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(source='module_id', read_only=True)
    room = RoomSerializer(source='room_id', read_only=True)
    staff = StaffSerializer(source='staff_id', read_only=True)
    
    class Meta:
        model = Timetable
        fields = [
            'timetable_id',
            'module_id',
            'room_id',
            'staff_id',
            'module',
            'room',
            'staff',
            'day_of_week',
            'start_time',
            'end_time',
            'semester'
        ]

class TeacherPreferenceSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff_id.staff_name', read_only=True)
    
    class Meta:
        model = TeacherPreference
        fields = [
            'preference_id',
            'staff_id',
            'staff_name',
            'day_of_week',
            'start_time',
            'end_time',
            'preference_weight'
        ]
        
    def validate(self, data):
        """
        Check that start_time is before end_time.
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError({
                "time_error": "End time must be after start time"
            })
        return data

class ConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conflict
        fields = [
            'conflict_id',
            'timetable_id_1',
            'timetable_id_2',
            'conflict_type',
            'conflict_description'
        ] 