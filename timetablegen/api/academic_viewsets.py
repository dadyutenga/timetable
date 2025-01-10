from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import Module, Program
from ..serializers import ModuleSerializer, ProgramSerializer
import csv
import io

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related('program_id').all()
    serializer_class = ModuleSerializer

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_csv(self, request):
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            created_modules = []
            
            for row in csv_data:
                program = Program.objects.get(program_id=row['program_id'])
                module = Module.objects.create(
                    module_code=row['module_code'],
                    module_name=row['module_name'],
                    program_id=program,
                    module_type=row.get('module_type', ''),
                    module_year=int(row['module_year']),
                    semester=int(row['semester']),
                    nta_level=row.get('nta_level', ''),
                    credits=int(row['credits']),
                    duration=int(row['duration'])
                )
                created_modules.append(ModuleSerializer(module).data)
            
            return Response({
                'message': 'Modules created successfully',
                'modules': created_modules
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related('dept_id').all()
    serializer_class = ProgramSerializer