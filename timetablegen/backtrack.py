from .models import Module, Room, Staff, Timetable, TeacherPreference, ClassModuleAllocation, Program
from django.db.models import Q
from datetime import datetime, timedelta
import random

class BacktrackTimetableGenerator:
    def __init__(self, academic_year, semester):
        self.academic_year = academic_year
        self.semester = semester
        self.timetable = []
        self.time_slots = self._generate_time_slots()
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.allocations = list(ClassModuleAllocation.objects.filter(academic_year=self.academic_year, semester=self.semester))

    def generate(self):
        if self._backtrack(0):
            return self.timetable
        return None

    def _backtrack(self, allocation_index):
        if allocation_index == len(self.allocations):
            return True

        allocation = self.allocations[allocation_index]
        module = allocation.module
        staff = allocation.staff
        available_slots = self._get_available_slots(staff)
        suitable_rooms = self._get_suitable_rooms(module)

        random.shuffle(available_slots)
        random.shuffle(suitable_rooms)

        for slot in available_slots:
            for room in suitable_rooms:
                if self._is_valid_assignment(module, staff, room, slot):
                    self._add_to_timetable(module, staff, room, slot)
                    if self._backtrack(allocation_index + 1):
                        return True
                    self._remove_last_entry()

        return False

    def _generate_time_slots(self):
        slots = []
        start = datetime.strptime("08:00", "%H:%M")
        end = datetime.strptime("18:00", "%H:%M")
        slot_duration = timedelta(hours=1)
        current = start
        while current < end:
            slots.append({
                'start_time': current.time(),
                'end_time': (current + slot_duration).time()
            })
            current += slot_duration
        return slots

    def _get_available_slots(self, staff):
        available_slots = []
        preferences = TeacherPreference.objects.filter(staff_id=staff)
        for day in self.days:
            for slot in self.time_slots:
                weight = self._get_preference_weight(preferences, day, slot)
                available_slots.append({
                    'day': day,
                    'start_time': slot['start_time'],
                    'end_time': slot['end_time'],
                    'weight': weight
                })
        return sorted(available_slots, key=lambda x: x['weight'], reverse=True)

    def _get_preference_weight(self, preferences, day, slot):
        for pref in preferences:
            if pref.day_of_week == day and pref.start_time <= slot['start_time'] < pref.end_time:
                return pref.preference_weight
        return 0

    def _get_suitable_rooms(self, module):
        program = Program.objects.get(modules=module)
        return Room.objects.filter(
            room_type=module.module_type,
            capacity__gte=program.program_capacity
        )

    def _is_valid_assignment(self, module, staff, room, slot):
        # Check for conflicts with existing timetable entries
        for entry in self.timetable:
            if entry['day_of_week'] == slot['day'] and self._time_overlap(entry, slot):
                if entry['staff_id'] == staff or entry['room_id'] == room:
                    return False

        # Check for consecutive classes in the same room
        previous_slot = self._get_previous_slot(slot)
        if previous_slot:
            previous_entry = next((e for e in self.timetable if e['day_of_week'] == slot['day'] and e['end_time'] == slot['start_time'] and e['room_id'] == room), None)
            if previous_entry and previous_entry['module_id'].dept_id != module.dept_id:
                return False

        return True

    def _time_overlap(self, entry1, entry2):
        return (entry1['start_time'] < entry2['end_time'] and entry2['start_time'] < entry1['end_time'])

    def _get_previous_slot(self, slot):
        index = self.time_slots.index(slot)
        if index > 0:
            return self.time_slots[index - 1]
        return None

    def _add_to_timetable(self, module, staff, room, slot):
        timetable_entry = Timetable(
            module_id=module,
            room_id=room,
            staff_id=staff,
            day_of_week=slot['day'],
            start_time=slot['start_time'],
            end_time=slot['end_time'],
            semester=self.semester
        )
        self.timetable.append(timetable_entry)

    def _remove_last_entry(self):
        if self.timetable:
            self.timetable.pop()

    def save_timetable(self):
        Timetable.objects.bulk_create(self.timetable)

def backtrack_timetable(academic_year, semester):
    generator = BacktrackTimetableGenerator(academic_year, semester)
    timetable = generator.generate()
    if timetable:
        generator.save_timetable()
        return True
    return False