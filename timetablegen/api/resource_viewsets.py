from rest_framework import viewsets
from ..models import Room, Staff
from ..serializers import RoomSerializer, StaffSerializer

class RoomViewSet(viewsets.ModelViewSet):
    """ViewSet for managing room resources."""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class StaffViewSet(viewsets.ModelViewSet):
    """ViewSet for managing staff resources."""
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
