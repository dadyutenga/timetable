from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Initialize the router
router = DefaultRouter()

# Register all viewsets
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'modules', views.ModuleViewSet, basename='module')
router.register(r'rooms', views.RoomViewSet, basename='room')
router.register(r'staff', views.StaffViewSet, basename='staff')
router.register(r'programs', views.ProgramViewSet, basename='program')
router.register(r'classes', views.ClassViewSet, basename='class')
router.register(r'timetables', views.TimetableViewSet, basename='timetable')
router.register(r'teacher-preferences', views.TeacherPreferenceViewSet, basename='teacher-preference')
router.register(r'module-allocations', views.ClassModuleAllocationViewSet, basename='module-allocation')
router.register(r'conflicts', views.ConflictViewSet, basename='conflict')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Custom endpoints for file uploads and bulk operations
    path('modules/upload/', 
         views.ModuleViewSet.as_view({'post': 'upload_csv'}),
         name='api-module-upload'),
         
    path('rooms/upload/', 
         views.RoomViewSet.as_view({'post': 'upload_csv'}),
         name='api-room-upload'),
         
    path('staff/upload/', 
         views.StaffViewSet.as_view({'post': 'upload_csv'}),
         name='api-staff-upload'),
         
    path('classes/upload/', 
         views.ClassViewSet.as_view({'post': 'upload_csv'}),
         name='api-class-upload'),
    
    path('timetables/generate/', 
         views.TimetableViewSet.as_view({'post': 'generate'}),
         name='api-timetable-generate'),
    
    path('teacher-preferences/bulk/', 
         views.TeacherPreferenceViewSet.as_view({'post': 'bulk_create'}),
         name='api-preference-bulk'),
    
    path('conflicts/by-type/', 
         views.ConflictViewSet.as_view({'get': 'by_type'}),
         name='api-conflicts-by-type'),
    
    path('module-allocations/bulk/', 
         views.ClassModuleAllocationViewSet.as_view({'post': 'bulk_create'}),
         name='api-allocation-bulk'),
]