from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ModuleViewSet,
    DepartmentViewSet,
    RoomViewSet,
    StaffViewSet,
    ProgramViewSet,
    ClassViewSet,
    ClassModuleAllocationViewSet,
    TimetableViewSet,
    TeacherPreferenceViewSet,
    ConflictViewSet
)

router = DefaultRouter()
router.register(r'modules', ModuleViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'module-allocations', ClassModuleAllocationViewSet)
router.register(r'timetables', TimetableViewSet)
router.register(r'teacher-preferences', TeacherPreferenceViewSet)
router.register(r'conflicts', ConflictViewSet)

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('modules/upload/', 
         ModuleViewSet.as_view({'post': 'upload_csv'}),
         name='api-module-upload'),
         
    path('rooms/upload/', 
         RoomViewSet.as_view({'post': 'upload_csv'}),
         name='api-room-upload'),
         
    path('staff/upload/', 
         StaffViewSet.as_view({'post': 'upload_csv'}),
         name='api-staff-upload'),
         
    path('classes/upload/', 
         ClassViewSet.as_view({'post': 'upload_csv'}),
         name='api-class-upload'),
    
    path('timetables/generate/', 
         TimetableViewSet.as_view({'post': 'generate'}),
         name='api-timetable-generate'),
    
    path('teacher-preferences/bulk/', 
         TeacherPreferenceViewSet.as_view({'post': 'bulk_create'}),
         name='api-preference-bulk'),
    
    path('conflicts/by-type/', 
         ConflictViewSet.as_view({'get': 'by_type'}),
         name='api-conflicts-by-type'),
    
    path('module-allocations/bulk/', 
         ClassModuleAllocationViewSet.as_view({'post': 'bulk_create'}),
         name='api-allocation-bulk'),
] 