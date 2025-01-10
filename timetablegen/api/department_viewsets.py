from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import Department
from ..serializers import DepartmentSerializer
import csv
import io

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_csv(self, request):
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            created_departments = []
            
            for row in csv_data:
                department = Department.objects.create(
                    dept_name=row['dept_name'],
                    dept_descr=row.get('dept_descr', ''),
                    hod=row.get('hod', ''),
                    hod_phone=row.get('hod_phone', ''),
                    hod_email=row.get('hod_email', '')
                )
                created_departments.append(DepartmentSerializer(department).data)
                
            return Response({
                'message': 'Departments created successfully',
                'departments': created_departments
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)