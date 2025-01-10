from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    dept_id = models.AutoField(primary_key=True)
    dept_name = models.CharField(max_length=255)
    dept_descr = models.TextField(blank=True, null=True)
    hod = models.CharField(max_length=255, blank=True, null=True)
    hod_phone = models.CharField(max_length=20, blank=True, null=True)
    hod_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.dept_name

class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_name = models.CharField(max_length=255)
    dept_id = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    nta_level = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.program_name

class Module(models.Model):
    module_id = models.AutoField(primary_key=True)
    module_code = models.CharField(max_length=50)
    module_name = models.CharField(max_length=255)
    module_type = models.CharField(max_length=50, blank=True, null=True)
    module_year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    nta_level = models.CharField(max_length=10, blank=True, null=True)
    module_credit = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.module_code} - {self.module_name}"

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    room_name = models.CharField(max_length=255)
    room_description = models.TextField(blank=True, null=True)
    room_type = models.CharField(max_length=50)
    capacity = models.IntegerField()
    building_name = models.CharField(max_length=255)
    room_no = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.room_name} ({self.room_no})"

class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    staff_name = models.CharField(max_length=255)
    rfid_id = models.CharField(max_length=50, blank=True, null=True)
    staff_email = models.EmailField(blank=True, null=True)
    staff_phone = models.CharField(max_length=20, blank=True, null=True)
    staff_type = models.CharField(max_length=50)
    staff_title = models.CharField(max_length=50, blank=True, null=True)
    dept_id = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='staff')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', null=True, blank=True)

    def __str__(self):
        return f"{self.staff_name} ({self.staff_title})"

class Timetable(models.Model):
    timetable_id = models.AutoField(primary_key=True)
    module_id = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='timetable_entries')
    room_id = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='timetable_entries')
    staff_id = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='timetable_entries')
    class_id = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='timetable_entries', null=True)
    class_stream = models.CharField(max_length=50, null=True, blank=True)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    semester = models.IntegerField()

    def __str__(self):
        return f"{self.module_id} - {self.class_id.Class_name} Stream {self.class_stream} ({self.day_of_week} {self.start_time}-{self.end_time})"

    class Meta:
        unique_together = [
            ['staff_id', 'day_of_week', 'start_time'],
            ['room_id', 'day_of_week', 'start_time'],
            ['class_id', 'class_stream', 'day_of_week', 'start_time']
        ]

class TeacherPreference(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='preferences')
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    preference_weight = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.staff_id} - {self.day_of_week} {self.start_time}-{self.end_time}"

class Class(models.Model):
    program_id = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='classes')
    Class_id = models.AutoField(primary_key=True)
    Class_name = models.CharField(max_length=50)
    class_capacity = models.IntegerField()
    academic_year = models.CharField(max_length=10)
    class_stream = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.Class_name} - {self.academic_year}"

class Conflict(models.Model):
    CONFLICT_TYPES = [
        ('Room', 'Room'),
        ('Teacher', 'Teacher'),
        ('Class', 'Class'),
    ]

    conflict_id = models.AutoField(primary_key=True)
    timetable_id_1 = models.ForeignKey(
        Timetable, 
        on_delete=models.CASCADE,
        related_name='conflicts_1'
    )
    timetable_id_2 = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE,
        related_name='conflicts_2'
    )
    conflict_type = models.CharField(
        max_length=10,
        choices=CONFLICT_TYPES
    )
    conflict_description = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.conflict_type}: {self.timetable_id_1} vs {self.timetable_id_2}"

    class Meta:
        db_table = 'conflicts'
        verbose_name = 'Conflict'
        verbose_name_plural = 'Conflicts'

class ClassModuleAllocation(models.Model):
    allocation_id = models.AutoField(primary_key=True)
    class_id = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='module_allocations')
    module_id = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='class_allocations')
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='teaching_allocations')
    program_id = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='class_allocations')

    class Meta:
        unique_together = ('class_id', 'module_id', 'staff_id')
        verbose_name = 'Class Module Allocation'
        verbose_name_plural = 'Class Module Allocations'

    def __str__(self):
        return f"Class: {self.class_id} | Module: {self.module_id} | Teacher: {self.staff_id}"