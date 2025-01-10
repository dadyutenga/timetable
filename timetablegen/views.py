import csv
import io
from django.shortcuts import render, redirect , get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy,  reverse
from .forms import ModuleForm, DepartmentForm, RoomForm, StaffForm , ProgramForm
from .models import Module, Program, Department, Room, TeacherPreference, Staff, Timetable, ClassModuleAllocation , Class
from .generator import TimetableGenerator
from django.views.generic import TemplateView, UpdateView , ListView , DeleteView
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def validate_file_size(value):
    limit = 25 * 1024 * 1024  # 25 MB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 25 MB.')

class AddModulesView( View):
    template_name = 'addModules.html'

    def get(self, request):
        form = ModuleForm()
        modules = Module.objects.select_related('program_id').all()
        return render(request, self.template_name, {
            'form': form, 
            'modules': modules,
            'user': request.user
        })

    def post(self, request):
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module added successfully')
            return redirect('addModules')

        return render(request, self.template_name, {'form': form, 'user': request.user})

class AddDepartmentsView( View):
    template_name = 'addDepts.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if 'csv_file' in request.FILES:
            return self.handle_csv_upload(request)
        else:
            return self.handle_single_department(request)

    def handle_single_department(self, request):
        dept_name = request.POST.get('dept_name')
        dept_descr = request.POST.get('dept_descr')
        hod = request.POST.get('hod')
        hod_phone = request.POST.get('hod_phone')
        hod_email = request.POST.get('hod_email')

        if dept_name:
            Department.objects.create(
                dept_name=dept_name,
                dept_descr=dept_descr,
                hod=hod,
                hod_phone=hod_phone,
                hod_email=hod_email
            )
            messages.success(request, 'Department added successfully.')
        else:
            messages.error(request, 'Department name is required.')

        return redirect('addDepts')

    def handle_csv_upload(self, request):
        csv_file = request.FILES['csv_file']
        try:
            FileExtensionValidator(allowed_extensions=['csv'])(csv_file)
            validate_file_size(csv_file)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('addDepts')

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            for row in csv_data:
                Department.objects.create(
                    dept_name=row['dept_name'],
                    dept_descr=row.get('dept_descr', ''),
                    hod=row.get('hod', ''),
                    hod_phone=row.get('hod_phone', ''),
                    hod_email=row.get('hod_email', '')
                )
            messages.success(request, 'Departments from CSV file added successfully.')
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
        return redirect('addDepts')

class AddRoomsView( View):
    template_name = 'addRooms.html'

    def get(self, request):
        rooms_list_url = reverse('rooms_list')
        departments = Department.objects.all()
        return render(request, self.template_name, {
            'rooms_list_url': rooms_list_url,
            'departments': departments
        })

    def post(self, request):
        if 'csv_file' in request.FILES:
            return self.handle_csv_upload(request)
        else:
            return self.handle_single_room(request)

    def handle_single_room(self, request):
        room_name = request.POST.get('room_name')
        room_description = request.POST.get('room_description')
        room_type = request.POST.get('room_type')
        capacity = request.POST.get('capacity')
        building_name = request.POST.get('building_name')
        room_no = request.POST.get('room_no')
        dept_id = request.POST.get('dept_id')

        if all([room_name, room_type, capacity, building_name, room_no]):
            Room.objects.create(
                room_name=room_name,
                room_description=room_description,
                room_type=room_type,
                capacity=capacity,
                building_name=building_name,
                room_no=room_no,
                dept_id_id=dept_id if dept_id else None
            )
            messages.success(request, 'Room added successfully.')
        else:
            messages.error(request, 'Please fill all required fields.')

        return redirect('addRooms')

    def handle_csv_upload(self, request):
        csv_file = request.FILES['csv_file']
        try:
            FileExtensionValidator(allowed_extensions=['csv'])(csv_file)
            validate_file_size(csv_file)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('addRooms')

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            for row in csv_data:
                Room.objects.create(
                    room_name=row['room_name'],
                    room_description=row.get('room_description', ''),
                    room_type=row['room_type'],
                    capacity=int(row['capacity']),
                    building_name=row['building_name'],
                    room_no=row['room_no']
                )
            messages.success(request, 'Rooms from CSV file added successfully.')
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
        return redirect('addRooms')
class AddStaffView(View):
    template_name = 'addStaff.html'

    def get(self, request):
        form = StaffForm()
        view_staff_url = reverse('viewStaff')  # Changed to 'viewStaff'
        return render(request, self.template_name, {
            'form': form, 
            'user': request.user,
            'view_staff_url': view_staff_url
        })

    def post(self, request):
        form = StaffForm(request.POST)
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            try:
                FileExtensionValidator(allowed_extensions=['csv'])(csv_file)
                validate_file_size(csv_file)
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('AddStaff')

            try:
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.reader(io.StringIO(decoded_file))
                next(csv_data)  # Skip the header row
                for row in csv_data:
                    department = Department.objects.get(dept_id=row[6])
                    Staff.objects.update_or_create(
                        staff_name=row[0],
                        defaults={
                            'rfid_id': row[1],
                            'staff_email': row[2],
                            'staff_phone': row[3],
                            'staff_type': row[4],
                            'staff_title': row[5],
                            'dept_id': department,
                        }
                    )
                messages.success(request, 'CSV file successfully processed')
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
            return redirect('AddStaff')

        elif form.is_valid():
            form.save()
            messages.success(request, 'Teacher added successfully')
            return redirect('AddStaff')

        view_staff_url = reverse('viewStaff')  # Changed to 'viewStaff'
        return render(request, self.template_name, {
            'form': form, 
            'user': request.user,
            'view_staff_url': view_staff_url
        })

def validate_file_size(value):
    limit = 25 * 1024 * 1024  # 25 MB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 25 MB.')
class AdminDashboardView( View):
    template_name = 'index.html'

    def get(self, request):
        return render(request, self.template_name)

class ModulesListView(LoginRequiredMixin, View):
    template_name = 'manage_modules.html'

    def get(self, request):
        modules = Module.objects.all()
        return render(request, self.template_name, {'modules': modules})

class DepartmentsListView(LoginRequiredMixin, View):
    template_name = 'view_departments.html'

    def get(self, request):
        departments = Department.objects.all()
        return render(request, self.template_name, {'departments': departments})

def generate_timetable_view(request):
    if request.method == "POST":
        dept_name = request.POST.get('dept')
        entry_year = request.POST.get('entry_year')
        academic_year = request.POST.get('academic_year')

        # Create an instance of TimetableGenerator and call the method
        generator = TimetableGenerator()
        generator.generate_timetable()

        return render(request, 'generate.html', {'message': 'Timetable generated successfully'})
    
    departments = Department.objects.all()
    return render(request, 'generate.html', {'departments': departments})

def view_timetable(request):
    if request.method == "POST":
        entry_year = request.POST.get('entry_year')
        dept_name = request.POST.get('dept')
        academic_year = request.POST.get('academic_year')

        try:
            dept = Department.objects.get(dept_name=dept_name)
            timetables = Timetable.objects.filter(
                module_id__program_id__dept_id=dept,
                semester=entry_year,
                academic_year=academic_year
            ).select_related(
                'module_id',
                'room_id',
                'staff_id',
                'class_id'
            ).order_by('day_of_week', 'start_time')

            return render(request, 'view_timetable.html', {
                'timetables': timetables,
                'dept': dept_name,
                'entry_year': entry_year,
                'academic_year': academic_year
            })
        except ObjectDoesNotExist:
            messages.error(request, 'Department not found')
            return redirect('view_timetable')

    departments = Department.objects.all()
    return render(request, 'view_timetable.html', {'departments': departments})

class StaffModuleAllocationView(View):
    template_name = 'staff_module_allocation.html'

    def get(self, request):
        staff = Staff.objects.select_related('dept_id').all()
        modules = Module.objects.select_related('program_id').all()
        allocations = ClassModuleAllocation.objects.select_related('staff_id', 'module_id').all()
        context = {
            'staff': staff,
            'modules': modules,
            'allocations': allocations,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        if 'csv_file' in request.FILES:
            return self.handle_csv_upload(request)
        else:
            return self.handle_single_allocation(request)

    def handle_single_allocation(self, request):
        staff_id = request.POST.get('staff')
        module_id = request.POST.get('module')

        if staff_id and module_id:
            try:
                staff = Staff.objects.get(pk=staff_id)
                module = Module.objects.get(pk=module_id)

                allocation, created = ClassModuleAllocation.objects.get_or_create(
                    staff=staff,
                    module=module
                )

                if created:
                    messages.success(request, 'Module allocated successfully.')
                else:
                    messages.info(request, 'This allocation already exists.')
            except ObjectDoesNotExist:
                messages.error(request, 'Staff or Module not found')
        else:
            messages.error(request, 'Please select both staff and module.')

        return redirect('staff_module_allocation')

    def handle_csv_upload(self, request):
        csv_file = request.FILES['csv_file']
        try:
            FileExtensionValidator(allowed_extensions=['csv'])(csv_file)
            validate_file_size(csv_file)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('staff_module_allocation')

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            successful_allocations = 0
            failed_allocations = 0

            for row in csv_data:
                try:
                    staff = Staff.objects.get(staff_id=row['staff_id'])
                    module = Module.objects.get(module_id=row['module_id'])

                    allocation, created = ClassModuleAllocation.objects.get_or_create(
                        staff=staff,
                        module=module
                    )

                    if created:
                        successful_allocations += 1
                    else:
                        failed_allocations += 1

                except ObjectDoesNotExist:
                    failed_allocations += 1

            messages.success(request, f'Successfully allocated {successful_allocations} modules. Failed: {failed_allocations}')
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
        return redirect('staff_module_allocation')

def add_classes(request):
    programs = Program.objects.all()

    if request.method == 'POST':
        if 'add_single' in request.POST:
            # Handle single class addition
            program_id = request.POST.get('program_id')
            class_name = request.POST.get('class_name')
            class_capacity = request.POST.get('class_capacity')
            academic_year = request.POST.get('academic_year')
            class_stream = request.POST.get('class_stream')

            Class.objects.create(
                program_id_id=program_id,
                Class_name=class_name,
                class_capacity=class_capacity,
                academic_year=academic_year,
                class_stream=class_stream
            )
            messages.success(request, 'Class added successfully.')

        elif 'upload_csv' in request.POST and request.FILES.get('csv_file'):
            # Handle CSV file upload
            csv_file = request.FILES['csv_file']

            # Validate file extension
            try:
                FileExtensionValidator(allowed_extensions=['csv'])(csv_file)
            except ValidationError:
                messages.error(request, 'Invalid file type. Please upload a CSV file.')
                return redirect('add_classes')

            # Validate file size
            try:
                validate_file_size(csv_file)
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('add_classes')

            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                for row in reader:
                    Class.objects.create(
                        program_id_id=row['program_id'],
                        Class_name=row['class_name'],
                        class_capacity=row['class_capacity'],
                        academic_year=row['academic_year'],
                        class_stream=row['class_stream']
                    )
                messages.success(request, 'Classes from CSV file added successfully.')
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')

        return redirect('add_classes')

    return render(request, 'addClasses.html', {'programs': programs})

    
class RegisterView(View):
    template_name = 'register.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('index')  # Redirect to the main page after successful registration
        return render(request, self.template_name, {'form': form})

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('index')  # Redirect to the main page after successful login
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, self.template_name)

class IndexView(TemplateView):
    template_name = 'index.html'

def logout_view(request):
    logout(request)
    return redirect('home')  

class EditModuleView( UpdateView):
    model = Module
    template_name = 'edit_module.html'
    fields = ['module_code', 'module_name', 'program_id', 'module_type', 'module_year', 'semester', 'nta_level']
    success_url = reverse_lazy('modules_list')  # Redirect to the list of modules after editing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Module'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Module updated successfully.')
        return super().form_valid(form)

class DepartmentListView( ListView):
    model = Department
    template_name = 'department_list.html'
    context_object_name = 'departments'

class EditDepartmentView(UpdateView):
    model = Department
    template_name = 'edit_department.html'
    fields = ['dept_name', 'dept_descr', 'hod', 'hod_phone', 'hod_email']
    success_url = reverse_lazy('department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Department'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully.')
        return super().form_valid(form)

class ViewStaffView(ListView):
    model = Staff
    template_name = 'viewStaff.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        return Staff.objects.select_related('dept_id').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class EditStaffView( UpdateView):
    model = Staff
    template_name = 'edit_staff.html'
    fields = ['staff_name', 'rfid_id', 'staff_email', 'staff_phone', 'staff_type', 'staff_title', 'dept_id']
    success_url = reverse_lazy('viewStaff')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Staff'
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Staff updated successfully.')
        return super().form_valid(form)

class DeleteStaffView( DeleteView):
    model = Staff
    template_name = 'delete_staff_confirm.html'
    success_url = reverse_lazy('viewStaff')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Staff'
        context['user'] = self.request.user
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f'Staff member "{self.get_object().staff_name}" has been deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
class RoomsListView(ListView):
    model = Room
    template_name = 'roomslist.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return Room.objects.all().order_by('room_no')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class DeleteRoomView(View):
    def post(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        room.delete()
        messages.success(request, f"Room {room.room_name} has been deleted successfully.")
        return redirect('rooms_list')
class ClassListView(ListView):
    model = Class
    template_name = 'classlist.html'
    context_object_name = 'classes'

    def get_queryset(self):
        return Class.objects.all().order_by('Class_name')

class DeleteClassView(View):
    def post(self, request, class_id):
        class_obj = get_object_or_404(Class, pk=class_id)
        class_obj.delete()
        messages.success(request, f"Class {class_obj.Class_name} has been deleted successfully.")
        return redirect('class_list')

class EditClassView(View):
    def get(self, request, class_id):
        class_obj = get_object_or_404(Class, pk=class_id)
        return render(request, 'edit_class.html', {'class': class_obj})

    def post(self, request, class_id):
        class_obj = get_object_or_404(Class, pk=class_id)
        # Update class fields based on form data
        class_obj.Class_name = request.POST.get('Class_name')
        class_obj.class_capacity = request.POST.get('class_capacity')
        class_obj.academic_year = request.POST.get('academic_year')
        class_obj.class_stream = request.POST.get('class_stream')
        class_obj.save()
        messages.success(request, f"Class {class_obj.Class_name} has been updated successfully.")
        return redirect('class_list')

class AddProgramsView(View):
    template_name = 'addProgram.html'

    def get(self, request):
        form = ProgramForm()
        programs = Program.objects.all()
        return render(request, self.template_name, {'form': form, 'programs': programs, 'user': request.user})

    def post(self, request):
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Program added successfully')
            return redirect('add_programs')
        programs = Program.objects.all()
        return render(request, self.template_name, {'form': form, 'programs': programs, 'user': request.user})

class TeacherPreferenceView(View):
    template_name = 'teacher_preferences.html'

    def get(self, request):
        staff = Staff.objects.select_related('dept_id').all()
        preferences = TeacherPreference.objects.select_related('staff_id').all()
        context = {
            'staff': staff,
            'preferences': preferences,
            'days': TeacherPreference.DAYS_OF_WEEK
        }
        return render(request, self.template_name, context)

    def post(self, request):
        staff_id = request.POST.get('staff_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        preference_weight = request.POST.get('preference_weight', 1)

        if all([staff_id, day_of_week, start_time, end_time]):
            TeacherPreference.objects.create(
                staff_id_id=staff_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                preference_weight=preference_weight
            )
            messages.success(request, 'Preference added successfully.')
        else:
            messages.error(request, 'Please fill all required fields.')

        return redirect('teacher_preferences')

# Add new view for conflicts
class ConflictListView(View):
    template_name = 'conflicts.html'

    def get(self, request):
        conflicts = Conflict.objects.select_related(
            'timetable_id_1__module_id',
            'timetable_id_1__staff_id',
            'timetable_id_1__room_id',
            'timetable_id_2__module_id',
            'timetable_id_2__staff_id',
            'timetable_id_2__room_id'
        ).all()
        return render(request, self.template_name, {'conflicts': conflicts})