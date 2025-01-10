from timetablegen.api.academic_viewsets import (
    ModuleViewSet,
    ProgramViewSet
)
from timetablegen.api.department_viewsets import DepartmentViewSet
from timetablegen.api.resource_viewsets import (
    RoomViewSet,
    StaffViewSet
)
from timetablegen.api.timetable_viewsets import (
    TimetableViewSet,
    TeacherPreferenceViewSet,
    ClassModuleAllocationViewSet,
    ClassViewSet,
    ConflictViewSet
)

__all__ = [
    'ModuleViewSet',
    'ProgramViewSet',
    'DepartmentViewSet',
    'RoomViewSet',
    'StaffViewSet',
    'TimetableViewSet',
    'TeacherPreferenceViewSet',
    'ClassModuleAllocationViewSet',
    'ClassViewSet',
    'ConflictViewSet',
]

# The ViewSets are now available to use in your URLs   