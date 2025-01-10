from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('admin_dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('add_modules/', views.AddModulesView.as_view(), name='addModules'),
    path('add_departments/', views.AddDepartmentsView.as_view(), name='addDepts'),
    path('add_rooms/', views.AddRoomsView.as_view(), name='addRooms'),
    path('add_staff/', views.AddStaffView.as_view(), name='addStaff'),
    path('add_classes/', views.add_classes, name='add_classes'),
    path('generate_timetable/', views.generate_timetable_view, name='generate'),
    path('view_timetable/', views.view_timetable, name='view_timetable'),
    path('staff_module_allocation/', views.StaffModuleAllocationView.as_view(), name='staff_module_allocation'),
    path('modules_list/', views.ModulesListView.as_view(), name='modules_list'),
    path('departments_list/', views.DepartmentsListView.as_view(), name='departments_list'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('add_staff/', views.AddStaffView.as_view(), name='addStaff'),
    path('add_modules/', views.AddModulesView.as_view(), name='addModules'),
    path('edit_course/', views.EditModuleView.as_view(), name='editModule'),  
    path('edit-module/<int:pk>/', views.EditModuleView.as_view(), name='edit_module'),
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('edit-department/<int:pk>/', views.EditDepartmentView.as_view(), name='editdepartment'),
    path('view-staff/', views.ViewStaffView.as_view(), name='viewStaff'),
    path('edit-staff/<int:pk>/', views.EditStaffView.as_view(), name='edit_staff'),
    path('delete-staff/<int:pk>/', views.DeleteStaffView.as_view(), name='delete_staff'),
    path('rooms_list/', views.RoomsListView.as_view(), name='rooms_list'),
    path('delete_room/<int:room_id>/', views.DeleteRoomView.as_view(), name='deleteroom'),
    path('add_classes/', views.add_classes, name='add_classes'),
    path('class_list/', views.ClassListView.as_view(), name='class_list'),
     path('add_programs/', views.AddProgramsView.as_view(), name='add_programs'),
    
]