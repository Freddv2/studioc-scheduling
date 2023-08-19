import argparse
import bisect
import math
from datetime import timedelta, datetime

import pandas as pd

from formatter import print_schedules, output_to_csv

best_schedule = {}
best_schedule_unassigned_students = {}
best_students_assignment_percentage = 0
best_teachers_assignment_percentage = 0


def possible_teachers(student, teachers):
    # Create a temporary list of teachers teaching the same instrument
    teachers_that_teach_instrument = [teacher for _, teacher in teachers.iterrows() if student['instrument'] == teacher['instrument']]

    # Sort the list so that preferred teachers come first
    teachers_that_teach_instrument.sort(key=lambda teacher: not student['preferred_teacher'] == teacher['teacher_name'])
    return teachers_that_teach_instrument


def assign_students(students, teachers):
    teachers_schedule = create_schedule(teachers)
    students.sort_values(by='current_student', ascending=False)
    unassigned_students = []

    # Assign students to teachers
    for _, student in students.iterrows():
        if not student['want_lesson']:
            continue
        for teacher in possible_teachers(student, teachers):
            if student['location'] != teacher['location'] and not student['can_be_realocated']:
                continue
            current_schedule = teachers_schedule[teacher['teacher_name']]

            # The order of time slots to try to assign
            student_schedule = {student['ideal_day']: create_time_slots(student['ideal_start_time'], student['ideal_end_time'])}
            add_to_schedule(student_schedule, student['alternative_day_1'], student['alternative_start_time_1'], student['alternative_end_time_1'])
            add_to_schedule(student_schedule, student['alternative_day_2'], student['alternative_start_time_2'], student['alternative_end_time_2'])
            add_to_schedule(student_schedule, student['alternative_day_3'], student['alternative_start_time_3'], student['alternative_end_time_3'])

            assigned = assign_to_available_slot(current_schedule, student_schedule, int(student['lesson_duration']) // 15, student, teacher)

            if assigned:
                break

        else:
            unassigned_students.append({'name': student['student_name'], 'email': student['email'], 'phone': student['phone_number']})

    update_best_iteration(teachers_schedule, unassigned_students)


def update_best_iteration(teachers_schedule, unassigned_students):
    student_matched_percent = round((1 - (len(unassigned_students) / len(students))) * 100, 1)
    teachers_assignment_percentage = calculate_teachers_assignment_percentage(teachers_schedule)

    global best_students_assignment_percentage
    if student_matched_percent > best_students_assignment_percentage:
        best_students_assignment_percentage = student_matched_percent
        global best_schedule
        best_schedule = teachers_schedule
        global best_schedule_unassigned_students
        best_schedule_unassigned_students = unassigned_students
        global best_teachers_assignment_percentage
        best_teachers_assignment_percentage = teachers_assignment_percentage


def calculate_teachers_assignment_percentage(teachers_schedule):
    total_percentage = 0
    total_teachers = len(teachers_schedule)

    for teacher, schedule in teachers_schedule.items():
        total_timeslots = len(schedule)
        timeslots_with_students = sum(1 for student_name in schedule.values() if student_name is not None)
        teacher_percentage = (timeslots_with_students / total_timeslots) * 100
        total_percentage += teacher_percentage

    teachers_assignment_percentage = round(total_percentage / total_teachers, 1)
    return teachers_assignment_percentage


def time_plus(time, minutes):
    start = datetime(
        2000, 1, 1,  # dummy date
        hour=time.hour, minute=time.minute, second=time.second
    )
    end = start + minutes
    return end.time()


def create_schedule(teachers):
    schedule = {}
    for _, teacher in teachers.iterrows():
        schedule.setdefault(teacher['teacher_name'], {})
        time = datetime.strptime(teacher['start_time'], '%H:%M').time()
        end_time = datetime.strptime(teacher['end_time'], '%H:%M').time()
        while time < end_time:
            schedule[teacher['teacher_name']][(teacher['day'], time)] = None
            time = time_plus(time, timedelta(minutes=15))
    return schedule


def create_time_slots(start_time, end_time):
    time_slots = []
    current_time = round_to_latest_15_minutes(datetime.strptime(start_time, '%H:%M'))
    rounded_end_time = round_to_soonest_15_minutes(datetime.strptime(end_time, '%H:%M'))
    while current_time <= rounded_end_time:
        time_slots.append(current_time.time())
        current_time = current_time + timedelta(minutes=15)
    return time_slots


def is_slot_available(schedule, day, quarter_hour_increments):
    return all((day, time) in schedule and schedule[(day, time)] is None for time in quarter_hour_increments)


def assign_student_to_slot(schedule, day, quarter_hour_increments, student, teacher):
    for time in quarter_hour_increments:
        schedule[(day, time)] = {'Name': student['student_name'], 'email': student['email'], 'phone': student['phone_number'], 'lesson_duration': student['lesson_duration'],
                                 'preferred_teacher': True if pd.isna(student['preferred_teacher']) or student['preferred_teacher'] == teacher['teacher_name'] else False}


def assign_to_available_slot(schedule, student_timeslots, lesson_duration_in_quarter_hours, student, teacher):
    for day, timeslots in student_timeslots.items():
        for timeslot in timeslots:
            lesson_start_time = [time_plus(timeslot, timedelta(minutes=15 * i)) for i in range(lesson_duration_in_quarter_hours)]
            if is_slot_available(schedule, day, lesson_start_time):
                assign_student_to_slot(schedule, day, lesson_start_time, student, teacher)
                return True
    return False


def students_preferred_teacher(student, teacher):
    return pd.isna(student['preferred_teacher']) or student['preferred_teacher'] == teacher['teacher_name']


def round_to_soonest_15_minutes(dt):
    closest = timedelta(minutes=15)
    return datetime.min + math.floor((dt - datetime.min) / closest) * closest


def round_to_latest_15_minutes(dt):
    closest = timedelta(minutes=15)
    return datetime.min + math.ceil((dt - datetime.min) / closest) * closest


def add_to_schedule(schedule, day, start_time, end_time):
    if day and not pd.isna(start_time) and not pd.isna(end_time):
        time_slots = create_time_slots(start_time, end_time)
        # If the day is not already in the schedule, add it with the time slot as the only item in the list
        if day not in schedule:
            schedule[day] = time_slots
            return

        # If the time slot is already in the list, do nothing
        for time_slot in time_slots:
            if time_slot in schedule[day]:
                continue
            else:
                bisect.insort(schedule[day], time_slot)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Studio C scheduling tool')
    parser.add_argument('-s', '--students_file', required=True, help='Path to the students CSV file')
    parser.add_argument('-t', '--teachers_file', required=True, help='Path to the teachers CSV file')
    parser.add_argument('-d', '--duration', type=int, required=True, help='Max scheduling duration in seconds')

    args = parser.parse_args()

    students = pd.read_csv(args.students_file)
    teachers = pd.read_csv(args.teachers_file)
    duration = args.duration
    start_time = datetime.now()
    iteration = 0
    schedule = {}
    while best_students_assignment_percentage < 100:
        shuffled_students = students.sample(frac=1).reset_index(drop=True)
        assign_students(shuffled_students, teachers)
        iteration += 1
        print(f' {iteration} iteration ran. Best Scheduling match is {best_students_assignment_percentage} %')
        if (datetime.now() - start_time).seconds >= duration:
            schedule = {teacher: {(day, time.strftime("%H:%M")): student for (day, time), student in timeslots.items()} for teacher, timeslots in best_schedule.items()}
            print(f'Unassigned students: {best_schedule_unassigned_students}')
            print(f'Student matched at {best_students_assignment_percentage}%.')
            print(f'Teachers matched at {best_teachers_assignment_percentage}%.')
            break

    print_schedules(schedule)
    output_to_csv(schedule, best_schedule_unassigned_students)
