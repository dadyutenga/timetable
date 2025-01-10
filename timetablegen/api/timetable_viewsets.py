from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import Timetable, TeacherPreference, ClassModuleAllocation, Class, Conflict
from ..serializers import (
    TimetableSerializer, 
    TeacherPreferenceSerializer,
    ClassModuleAllocationSerializer,
    ClassSerializer,
    ConflictSerializer
)

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.select_related(
        'module_id',
        'room_id',
        'staff_id',
        'class_id'
    ).all()
    serializer_class = TimetableSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        try:
            # Add your timetable generation logic here
            return Response({
                'message': 'Timetable generated successfully'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TeacherPreferenceViewSet(viewsets.ModelViewSet):
    queryset = TeacherPreference.objects.select_related('staff_id').all()
    serializer_class = TeacherPreferenceSerializer

class ClassModuleAllocationViewSet(viewsets.ModelViewSet):
    queryset = ClassModuleAllocation.objects.select_related('module_id', 'staff_id').all()
    serializer_class = ClassModuleAllocationSerializer

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.select_related('program_id').all()
    serializer_class = ClassSerializer

class ConflictViewSet(viewsets.ModelViewSet):
    queryset = Conflict.objects.select_related(
        'timetable_id_1',
        'timetable_id_2'
    ).all()
    serializer_class = ConflictSerializer

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        conflict_type = request.query_params.get('type')
        if conflict_type:
            conflicts = self.queryset.filter(conflict_type=conflict_type)
            serializer = self.get_serializer(conflicts, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Conflict type not provided'},
            status=status.HTTP_400_BAD_REQUEST
        )