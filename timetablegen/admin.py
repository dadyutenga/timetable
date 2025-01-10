from django.contrib import admin
from .models import Department, Module, Program, Room, Staff, Timetable, TeacherPreference

admin.site.register(Department)
admin.site.register(Module)
admin.site.register(Program)
admin.site.register(Room)
admin.site.register(Staff)
admin.site.register(Timetable)
admin.site.register(TeacherPreference)