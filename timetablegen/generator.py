from datetime import datetime, timedelta, time
import random
from typing import Dict, List, Set, Tuple, Optional
from django.db import transaction
from django.core.cache import cache
from collections import defaultdict
from dataclasses import dataclass
import heapq

from .models import (
    Timetable, Module, Room, Staff, Class, 
    ClassModuleAllocation, Conflict,
    Program
)

@dataclass
class SchedulingPriority:
    """Defines priority levels for scheduling different types of classes"""
    HIGH = 3    # Core modules, labs
    MEDIUM = 2  # Regular modules
    LOW = 1     # Optional modules

class TimeSlot:
    def __init__(self, day: str, start_time: time, end_time: time):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time

    def overlaps(self, other: 'TimeSlot') -> bool:
        return self.day == other.day and (
            self.start_time < other.end_time and other.start_time < self.end_time
        )

class TimetableGenerator:
    """Comprehensive timetable generation system"""
    
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.conflict_detector = ConflictDetector()
        
        # Track allocations and workloads
        self.staff_workload: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.stream_allocations: Dict[int, List[TimeSlot]] = defaultdict(list)
        self.room_type_usage: Dict[str, Dict[int, List[TimeSlot]]] = defaultdict(lambda: defaultdict(list))
        
        # Cache frequently accessed data
        self.module_credits = self._cache_module_credits()
        self.room_capacities = self._cache_room_capacities()
        
        # Scheduling queues
        self.pending_allocations: List[Tuple[int, ClassModuleAllocation]] = []
        self.failed_allocations: List[Tuple[int, ClassModuleAllocation]] = []

    def _cache_module_credits(self) -> Dict[int, int]:
        """Cache module credits for quick access"""
        return {
            module.module_id: module.module_credit 
            for module in Module.objects.all()
        }

    def _cache_room_capacities(self) -> Dict[int, int]:
        """Cache room capacities for quick access"""
        return {
            room.room_id: room.capacity 
            for room in Room.objects.all()
        }

    def generate_timetable(self):
        """Main timetable generation process"""
        try:
            with transaction.atomic():
                # 1. Prepare allocations
                self._prepare_allocations()
                
                # 2. Generate initial schedule
                self._generate_initial_schedule()
                
                # 3. Optimize and resolve conflicts
                self._optimize_schedule()
                
                # 4. Handle failed allocations
                self._handle_failed_allocations()
                
                # 5. Validate final schedule
                if not self._validate_final_schedule():
                    raise ValueError("Failed to generate valid timetable")
                
                # 6. Save to database
                self._save_timetable()
                
        except Exception as e:
            print(f"Timetable generation failed: {str(e)}")
            raise

    def _prepare_allocations(self):
        """Prepare and prioritize allocations"""
        allocations = ClassModuleAllocation.objects.select_related(
            'class_id', 'module_id', 'staff_id', 'program_id'
        ).all()

        # Group allocations by program and prioritize
        for allocation in allocations:
            priority = self._calculate_priority(allocation)
            heapq.heappush(self.pending_allocations, (-priority, allocation))

    def _calculate_priority(self, allocation: ClassModuleAllocation) -> int:
        """Calculate scheduling priority for an allocation"""
        base_priority = SchedulingPriority.MEDIUM
        
        # Adjust priority based on module credits
        credit = self.module_credits.get(allocation.module_id.module_id, 10)
        if credit > 14:
            base_priority = SchedulingPriority.HIGH
        elif credit < 8:
            base_priority = SchedulingPriority.LOW

        # Adjust for module type (labs get higher priority)
        if allocation.module_id.module_type == 'Laboratory':
            base_priority += 1

        # Adjust for program level
        if allocation.program_id.nta_level in ['7', '8', '9']:  # Bachelor's and Master's
            base_priority += 1

        return base_priority

    def _generate_initial_schedule(self):
        """Generate initial schedule using greedy algorithm"""
        while self.pending_allocations:
            _, allocation = heapq.heappop(self.pending_allocations)
            
            # Find suitable time slots
            possible_slots = self._find_possible_slots(allocation)
            
            if not possible_slots:
                self.failed_allocations.append((SchedulingPriority.HIGH, allocation))
                continue

            # Try to schedule
            success = self._schedule_allocation(allocation, possible_slots)
            if not success:
                self.failed_allocations.append((SchedulingPriority.HIGH, allocation))

    def _find_possible_slots(self, allocation: ClassModuleAllocation) -> List[TimeSlot]:
        """Find all possible time slots for an allocation"""
        possible_slots = []
        program_constraints = TimetableConstraints.PROGRAM_CONSTRAINTS[
            allocation.program_id.program_name
        ]

        for day in TimetableConstraints.DAYS:
            current_time = program_constraints['start_time']
            
            while current_time < program_constraints['end_time']:
                # Skip break times
                if (TimetableConstraints.BREAKFAST_START <= current_time < 
                    TimetableConstraints.BREAKFAST_END):
                    current_time = TimetableConstraints.BREAKFAST_END
                    continue
                    
                if (TimetableConstraints.LUNCH_START <= current_time < 
                    TimetableConstraints.LUNCH_END):
                    current_time = TimetableConstraints.LUNCH_END
                    continue

                # Calculate end time based on module credits
                duration = self._calculate_duration(allocation)
                end_time = (datetime.combine(datetime.today(), current_time) + 
                           duration).time()

                if end_time > program_constraints['end_time']:
                    break

                slot = TimeSlot(day, current_time, end_time)
                
                # Check availability
                if self._is_slot_available(allocation, slot):
                    possible_slots.append(slot)

                # Move to next potential slot
                current_time = end_time

        return possible_slots

    def _calculate_duration(self, allocation: ClassModuleAllocation) -> timedelta:
        """Calculate class duration based on module credits"""
        credit = self.module_credits.get(allocation.module_id.module_id, 10)
        
        if credit <= 10:
            return TimetableConstraints.MIN_DURATION
        elif credit >= 15:
            return TimetableConstraints.MAX_DURATION
        else:
            return timedelta(hours=2, minutes=30)

    def _is_slot_available(self, allocation: ClassModuleAllocation, slot: TimeSlot) -> bool:
        """Check if a time slot is available for all resources"""
        return (
            self.resource_manager.is_staff_available(
                allocation.staff_id.staff_id, slot
            ) and
            self.resource_manager.is_class_available(
                allocation.class_id.Class_id, slot
            ) and
            self._find_available_room(allocation, slot) is not None
        )

    def _find_available_room(
        self, 
        allocation: ClassModuleAllocation, 
        slot: TimeSlot
    ) -> Optional[Room]:
        """Find an available room suitable for the allocation"""
        # Get suitable rooms based on module type and class size
        suitable_rooms = Room.objects.filter(
            room_type=allocation.module_id.module_type,
            capacity__gte=allocation.class_id.class_capacity
        )

        # Check availability for each room
        for room in suitable_rooms:
            if self.resource_manager.is_room_available(room.room_id, slot):
                return room

        return None

    def _optimize_schedule(self):
        """Optimize the generated schedule"""
        self._optimize_staff_workload()
        self._optimize_room_usage()
        self._optimize_stream_distribution()
        self._resolve_conflicts()

    def _optimize_staff_workload(self):
        """Balance and optimize staff workload distribution"""
        staff_daily_slots = defaultdict(lambda: defaultdict(list))
        
        # Group slots by staff and day
        for staff_id, schedule in self.resource_manager.staff_schedule.items():
            for slot in schedule:
                staff_daily_slots[staff_id][slot.day].append(slot)

        # Optimize each staff's schedule
        for staff_id, daily_schedule in staff_daily_slots.items():
            for day, slots in daily_schedule.items():
                # Sort slots by start time
                slots.sort(key=lambda x: x.start_time)
                
                # Check for excessive gaps
                self._minimize_staff_gaps(staff_id, day, slots)
                
                # Check for excessive consecutive hours
                self._balance_consecutive_hours(staff_id, day, slots)

    def _minimize_staff_gaps(self, staff_id: int, day: str, slots: List[TimeSlot]):
        """Minimize gaps in staff's daily schedule"""
        if len(slots) <= 1:
            return

        for i in range(len(slots) - 1):
            gap = datetime.combine(datetime.today(), slots[i+1].start_time) - \
                  datetime.combine(datetime.today(), slots[i].end_time)
            
            if timedelta(minutes=30) < gap < timedelta(hours=2):
                # Try to reschedule one of the slots
                self._try_reschedule_slot(staff_id, day, slots[i], slots[i+1])

    def _balance_consecutive_hours(self, staff_id: int, day: str, slots: List[TimeSlot]):
        """Balance consecutive teaching hours"""
        consecutive_hours = timedelta()
        consecutive_slots = []

        for slot in slots:
            if not consecutive_slots or self._is_consecutive(consecutive_slots[-1], slot):
                consecutive_slots.append(slot)
                consecutive_hours += (datetime.combine(datetime.today(), slot.end_time) - 
                                   datetime.combine(datetime.today(), slot.start_time))
            else:
                if consecutive_hours > timedelta(hours=4):
                    # Try to split consecutive slots
                    self._split_consecutive_slots(staff_id, consecutive_slots)
                consecutive_slots = [slot]
                consecutive_hours = (datetime.combine(datetime.today(), slot.end_time) - 
                                  datetime.combine(datetime.today(), slot.start_time))

    def _optimize_stream_distribution(self):
        """Optimize distribution of parallel streams"""
        # Group allocations by class
        class_streams = defaultdict(list)
        for allocation_id, slots in self.stream_allocations.items():
            allocation = ClassModuleAllocation.objects.get(allocation_id=allocation_id)
            class_streams[allocation.class_id.Class_id].extend(slots)

        # Process each class's streams
        for class_id, slots in class_streams.items():
            self._synchronize_streams(class_id, slots)
            self._balance_stream_distribution(class_id, slots)

    def _synchronize_streams(self, class_id: int, slots: List[TimeSlot]):
        """Synchronize parallel streams of the same class"""
        # Group slots by module
        module_slots = defaultdict(list)
        for slot in slots:
            module_slots[slot.module_id].append(slot)

        # Process each module's slots
        for module_id, module_slots in module_slots.items():
            if len(module_slots) > 1:  # Multiple streams
                self._align_parallel_streams(class_id, module_id, module_slots)

    def _align_parallel_streams(self, class_id: int, module_id: int, slots: List[TimeSlot]):
        """Align parallel streams to run consecutively"""
        slots.sort(key=lambda x: x.start_time)
        target_start_time = slots[0].start_time

        for i, slot in enumerate(slots):
            if i > 0:
                desired_start = (datetime.combine(datetime.today(), slots[i-1].end_time) + 
                               timedelta(minutes=15)).time()
                if slot.start_time != desired_start:
                    self._reschedule_stream(slot, desired_start)

    def _reschedule_stream(self, slot: TimeSlot, desired_start_time: datetime.time):
        """Attempt to reschedule a stream to a desired start time"""
        duration = datetime.combine(datetime.today(), slot.end_time) - \
                  datetime.combine(datetime.today(), slot.start_time)
        desired_end_time = (datetime.combine(datetime.today(), desired_start_time) + 
                           duration).time()
        
        new_slot = TimeSlot(slot.day, desired_start_time, desired_end_time)
        
        # Check if new slot is available
        allocation = self._get_allocation_for_slot(slot)
        if allocation and self._is_slot_available(allocation, new_slot):
            self._update_slot_assignment(slot, new_slot, allocation)

    def _optimize_room_usage(self):
        """Optimize room usage and minimize room changes"""
        # Group allocations by class and day
        class_daily_rooms = defaultdict(lambda: defaultdict(list))
        
        for allocation_id, slots in self.stream_allocations.items():
            for slot in slots:
                allocation = ClassModuleAllocation.objects.get(allocation_id=allocation_id)
                class_daily_rooms[allocation.class_id.Class_id][slot.day].append(
                    (slot, self._get_room_for_slot(slot))
                )

        # Optimize room assignments
        for class_id, daily_schedule in class_daily_rooms.items():
            for day, slots_and_rooms in daily_schedule.items():
                self._optimize_daily_room_usage(class_id, day, slots_and_rooms)

    def _optimize_daily_room_usage(
        self, 
        class_id: int, 
        day: str, 
        slots_and_rooms: List[Tuple[TimeSlot, Room]]
    ):
        """Optimize room usage for a class on a specific day"""
        slots_and_rooms.sort(key=lambda x: x[0].start_time)
        
        # Try to keep consecutive slots in the same room
        current_room = None
        consecutive_slots = []

        for slot, room in slots_and_rooms:
            if not current_room:
                current_room = room
                consecutive_slots = [slot]
            elif room.room_id != current_room.room_id:
                # Try to move to the previous room if possible
                if self._can_use_room_for_slots([slot], current_room):
                    self._update_room_assignment(slot, current_room)
                else:
                    # Try to move previous slots to new room
                    if self._can_use_room_for_slots(consecutive_slots, room):
                        for prev_slot in consecutive_slots:
                            self._update_room_assignment(prev_slot, room)
                        current_room = room
                    consecutive_slots = [slot]
            else:
                consecutive_slots.append(slot)

    def _resolve_conflicts(self):
        """Resolve any remaining scheduling conflicts"""
        conflicts = self._detect_all_conflicts()
        
        while conflicts:
            for conflict in conflicts:
                if not self._resolve_single_conflict(conflict):
                    # If can't resolve, add to failed allocations
                    allocation = self._get_allocation_for_slot(conflict.timetable_id_1)
                    self.failed_allocations.append((SchedulingPriority.HIGH, allocation))
            
            # Check for remaining conflicts
            conflicts = self._detect_all_conflicts()

    def _detect_all_conflicts(self) -> List[Conflict]:
        """Detect all types of conflicts in the current schedule"""
        conflicts = []
        
        # Check staff conflicts
        staff_conflicts = self._detect_staff_conflicts()
        conflicts.extend(staff_conflicts)
        
        # Check room conflicts
        room_conflicts = self._detect_room_conflicts()
        conflicts.extend(room_conflicts)
        
        # Check stream conflicts
        stream_conflicts = self._detect_stream_conflicts()
        conflicts.extend(stream_conflicts)
        
        return conflicts

    def _detect_staff_conflicts(self) -> List[Conflict]:
        """Detect staff double-booking conflicts"""
        conflicts = []
        staff_slots = defaultdict(list)
        
        # Group slots by staff
        for staff_id, schedule in self.resource_manager.staff_schedule.items():
            for slot in schedule:
                staff_slots[staff_id].append(slot)
        
        # Check for overlaps
        for staff_id, slots in staff_slots.items():
            for i, slot1 in enumerate(slots):
                for slot2 in slots[i+1:]:
                    if slot1.overlaps(slot2):
                        conflicts.append(
                            Conflict(
                                timetable_id_1=self._get_timetable_entry(slot1),
                                timetable_id_2=self._get_timetable_entry(slot2),
                                conflict_type='staff',
                                conflict_description=f"staff {staff_id} double-booked"
                            )
                        )
        
        return conflicts

    def _resolve_single_conflict(self, conflict: Conflict) -> bool:
        """Attempt to resolve a single conflict"""
        if conflict.conflict_type == 'staff':
            return self._resolve_staff_conflict(conflict)
        elif conflict.conflict_type == 'Room':
            return self._resolve_room_conflict(conflict)
        elif conflict.conflict_type == 'Stream':
            return self._resolve_stream_conflict(conflict)
        return False

    def _resolve_staff_conflict(self, conflict: Conflict) -> bool:
        """Resolve a staff conflict by rescheduling one of the slots"""
        slot1 = self._get_slot_from_timetable(conflict.timetable_id_1)
        slot2 = self._get_slot_from_timetable(conflict.timetable_id_2)
        
        # Try to reschedule slot1
        allocation1 = self._get_allocation_for_slot(slot1)
        alternative_slots = self._find_possible_slots(allocation1)
        
        for alt_slot in alternative_slots:
            if self._try_reschedule_slot_to(slot1, alt_slot):
                return True
        
        # If slot1 couldn't be rescheduled, try slot2
        allocation2 = self._get_allocation_for_slot(slot2)
        alternative_slots = self._find_possible_slots(allocation2)
        
        for alt_slot in alternative_slots:
            if self._try_reschedule_slot_to(slot2, alt_slot):
                return True
        
        return False

    def _handle_failed_allocations(self):
        """Handle allocations that couldn't be scheduled"""
        retry_count = 0
        max_retries = 3
        
        while self.failed_allocations and retry_count < max_retries:
            failed = []
            
            # Sort failed allocations by priority
            self.failed_allocations.sort(reverse=True)
            
            for priority, allocation in self.failed_allocations:
                # Try with relaxed constraints
                if self._try_schedule_with_relaxed_constraints(allocation):
                    continue
                
                # If still failed, add to new failed list
                failed.append((priority, allocation))
            
            self.failed_allocations = failed
            retry_count += 1

    def _try_schedule_with_relaxed_constraints(self, allocation: ClassModuleAllocation) -> bool:
        """Attempt to schedule with relaxed constraints"""
        # Try different strategies with increasingly relaxed constraints
        strategies = [
            self._try_different_room_type,
            self._try_split_session,
            self._try_different_day,
            self._try_edge_hours
        ]
        
        for strategy in strategies:
            if strategy(allocation):
                return True
        
        return False

    def _validate_final_schedule(self) -> bool:
        """Validate the final schedule"""
        # Check for basic constraints
        if not self._validate_basic_constraints():
            return False
        
        # Check staff workload
        if not self._validate_staff_workload():
            return False
        
        # Check stream distribution
        if not self._validate_stream_distribution():
            return False
        
        # Check room utilization
        if not self._validate_room_utilization():
            return False
        
        return True

    def _validate_basic_constraints(self) -> bool:
        """Validate basic scheduling constraints"""
        for allocation_id, slots in self.stream_allocations.items():
            allocation = ClassModuleAllocation.objects.get(allocation_id=allocation_id)
            
            # Check number of periods
            if not self._validate_period_count(allocation, slots):
                return False
            
            # Check time constraints
            if not self._validate_time_constraints(allocation, slots):
                return False
            
            # Check break times
            if not self._validate_break_times(slots):
                return False
        
        return True

    def _save_timetable(self):
        """Save the generated timetable to the database"""
        with transaction.atomic():
            # Clear existing timetable entries
            Timetable.objects.all().delete()
            
            # Save new timetable entries
            timetable_entries = []
            
            for allocation_id, slots in self.stream_allocations.items():
                allocation = ClassModuleAllocation.objects.get(allocation_id=allocation_id)
                
                for slot in slots:
                    room = self._get_room_for_slot(slot)
                    
                    timetable_entries.append(
                        Timetable(
                            module_id=allocation.module_id,
                            room_id=room,
                            staff_id=allocation.staff_id,
                            class_id=allocation.class_id,
                            class_stream=allocation.class_id.class_stream,
                            day_of_week=slot.day,
                            start_time=slot.start_time,
                            end_time=slot.end_time,
                            semester=allocation.module_id.semester
                        )
                    )
            
            # Bulk create timetable entries
            Timetable.objects.bulk_create(timetable_entries)
