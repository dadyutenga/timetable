from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .forms import ModuleForm, DepartmentForm, RoomForm, StaffForm, ProgramForm
from .models import Module, Program, Department, Room, TeacherPreference, Staff, Timetable, ClassModuleAllocation, Class
from .generator import TimetableGenerator
from django.core.validators import FileExtensionValidator
import csv
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .serializers import *
from .models import *
from .generator import TimetableGenerator

def validate_file_size(value):
    limit = 25 * 1024 * 1024  # 25 MB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 25 MB.')

class AddModulesView(View):
    def get(self, request):
        modules = Module.objects.select_related('program_id').all()
        return JsonResponse({
            'modules': list(modules.values())
        })

    def post(self, request):
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Module added successfully',
                'module': {
                    'id': module.id,
                    'name': module.module_name,
                    # Add other relevant fields
                }
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

class AddDepartmentsView(View):
    def post(self, request):
        if 'csv_file' in request.FILES:
            return self.handle_csv_upload(request)
        return self.handle_single_department(request)

    def handle_single_department(self, request):
        try:
            dept = Department.objects.create(
                dept_name=request.POST.get('dept_name'),
                dept_descr=request.POST.get('dept_descr'),
                hod=request.POST.get('hod'),
                hod_phone=request.POST.get('hod_phone'),
                hod_email=request.POST.get('hod_email')
            )
            return JsonResponse({
                'success': True,
                'message': 'Department added successfully',
                'department': {
                    'id': dept.id,
                    'name': dept.dept_name
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    # ... rest of the CSV handling methods remain similar but return JsonResponse ...

# Continue converting other views similarly, replacing render() with JsonResponse()
# Example of a converted list view:
class ModulesListView(LoginRequiredMixin, View):
    def get(self, request):
        modules = Module.objects.all()
        return JsonResponse({
            'modules': list(modules.values())
        })

# Example of a converted generator view:
def generate_timetable_view(request):
    if request.method == "POST":
        try:
            generator = TimetableGenerator()
            result = generator.generate_timetable()
            return JsonResponse({
                'success': True,
                'message': 'Timetable generated successfully',
                'data': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'departments': list(Department.objects.values())
    })

class AddRoomsView(View):
    def get(self, request):
        rooms = Room.objects.all()
        return JsonResponse({
            'rooms': list(rooms.values())
        })

    def post(self, request):
        if 'csv_file' in request.FILES:
            return self.handle_csv_upload(request)
        return self.handle_single_room(request)

    def handle_single_room(self, request):
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Room added successfully',
                'room': {
                    'id': room.id,
                    'name': room.room_name,
                    'capacity': room.capacity
                }
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

class AddStaffView(View):
    def get(self, request):
        staff = Staff.objects.select_related('dept_id').all()
        return JsonResponse({
            'staff': list(staff.values())
        })

    def post(self, request):
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Staff member added successfully',
                'staff': {
                    'id': staff.id,
                    'name': staff.staff_name,
                    'email': staff.staff_email
                }
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

class StaffModuleAllocationView(LoginRequiredMixin, View):
    def get(self, request):
        allocations = TeacherPreference.objects.select_related('staff_id', 'module_id').all()
        return JsonResponse({
            'allocations': list(allocations.values(
                'id',
                'staff_id__staff_name',
                'module_id__module_name',
                'preference_level'
            ))
        })

    def post(self, request):
        try:
            staff_id = request.POST.get('staff_id')
            module_id = request.POST.get('module_id')
            preference_level = request.POST.get('preference_level')

            allocation = TeacherPreference.objects.create(
                staff_id_id=staff_id,
                module_id_id=module_id,
                preference_level=preference_level
            )

            return JsonResponse({
                'success': True,
                'message': 'Module allocated successfully',
                'allocation': {
                    'id': allocation.id,
                    'staff': allocation.staff_id.staff_name,
                    'module': allocation.module_id.module_name
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

class DepartmentsListView(LoginRequiredMixin, View):
    def get(self, request):
        departments = Department.objects.all()
        return JsonResponse({
            'departments': list(departments.values())
        })

def view_timetable(request):
    try:
        timetables = Timetable.objects.select_related(
            'module_id',
            'room_id',
            'staff_id'
        ).all()
        
        return JsonResponse({
            'success': True,
            'timetables': list(timetables.values(
                'id',
                'day',
                'start_time',
                'end_time',
                'module_id__module_name',
                'room_id__room_name',
                'staff_id__staff_name'
            ))
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def add_classes(request):
    if request.method == "POST":
        try:
            program_id = request.POST.get('program_id')
            year = request.POST.get('year')
            semester = request.POST.get('semester')

            class_obj = Class.objects.create(
                program_id_id=program_id,
                year=year,
                semester=semester
            )

            return JsonResponse({
                'success': True,
                'message': 'Class added successfully',
                'class': {
                    'id': class_obj.id,
                    'program': class_obj.program_id.program_name,
                    'year': class_obj.year,
                    'semester': class_obj.semester
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET request
    programs = Program.objects.all()
    return JsonResponse({
        'programs': list(programs.values())
    })

# Continue converting other views...

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        try:
            # CSV upload logic here
            return Response({'message': 'Departments imported successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        try:
            # CSV upload logic here
            return Response({'message': 'Modules imported successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_program(self, request):
        program_id = request.query_params.get('program_id')
        modules = self.queryset.filter(program_id=program_id)
        serializer = self.serializer_class(modules, many=True)
        return Response(serializer.data)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        try:
            # CSV upload logic here
            return Response({'message': 'Rooms imported successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        try:
            # CSV upload logic here
            return Response({'message': 'Staff imported successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        try:
            # CSV upload logic here
            return Response({'message': 'Classes imported successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate(self, request):
        try:
            generator = TimetableGenerator()
            result = generator.generate_timetable()
            return Response({
                'message': 'Timetable generated successfully',
                'data': result
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TeacherPreferenceViewSet(viewsets.ModelViewSet):
    queryset = TeacherPreference.objects.all()
    serializer_class = TeacherPreferenceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        try:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({'message': 'Preferences created successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ConflictViewSet(viewsets.ModelViewSet):
    queryset = Conflict.objects.all()
    serializer_class = ConflictSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        conflict_type = request.query_params.get('type')
        conflicts = self.queryset.filter(conflict_type=conflict_type)
        serializer = self.serializer_class(conflicts, many=True)
        return Response(serializer.data)

class ClassModuleAllocationViewSet(viewsets.ModelViewSet):
    queryset = ClassModuleAllocation.objects.all()
    serializer_class = ClassModuleAllocationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        try:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({'message': 'Allocations created successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)