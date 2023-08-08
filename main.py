import bisect
import argparse
import math
from datetime import timedelta, datetime

from matplotlib import pyplot as plt

from formatter import format_schedule

import pandas as pd
import seaborn as sns

best_schedule = {}
best_schedule_unassigned_students = {}
best_schedule_match_percent = 0


def assign_students(students, teachers):
    teachers_schedule = create_schedule(teachers)
    students.sort_values(by='current_student', ascending=False)
    unassigned_students = []

    # Assign students to teachers
    for _, student in students.iterrows():
        if not student['want_lesson']:
            continue
        for _, teacher in teachers.iterrows():
            if student['instrument'] != teacher['instrument']:
                continue
            if not students_preferred_teacher(student, teacher):
                continue
            if student['location'] != teacher['location']:
                continue
            current_schedule = teachers_schedule[teacher['teacher_name']]

            # The order of time slots to try to assign
            student_schedule = {student['ideal_day']: create_time_slots(student['ideal_start_time'], student['ideal_end_time'])}
            add_to_schedule(student_schedule, student['alternative_day_1'], student['alternative_start_time_1'], student['alternative_end_time_1'])
            add_to_schedule(student_schedule, student['alternative_day_2'], student['alternative_start_time_2'], student['alternative_end_time_2'])
            add_to_schedule(student_schedule, student['alternative_day_3'], student['alternative_start_time_3'], student['alternative_end_time_3'])

            assigned = assign_to_available_slot(current_schedule, student_schedule, int(student['lesson_duration']) // 15, student['student_name'])

            if not assigned:
                unassigned_students.append(student['student_name'])
        else:
            unassigned_students.append(student['student_name'])

    percent_matched = round((len(unassigned_students) / len(students)) * 100, 1)
    update_best_iteration(percent_matched, teachers_schedule, unassigned_students)


def update_best_iteration(percent_matched, teacher_schedule, unassigned_students):
    global best_schedule_match_percent
    if percent_matched > best_schedule_match_percent:
        best_schedule_match_percent = percent_matched
        global best_schedule
        best_schedule = teacher_schedule
        global best_schedule_unassigned_students
        best_schedule_unassigned_students = unassigned_students


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
        schedule[teacher['teacher_name']] = {}
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
    return all(schedule.get((day, time), None) is None for time in quarter_hour_increments)


def assign_student_to_slot(schedule, day, quarter_hour_increments, student_name):
    for time in quarter_hour_increments:
        schedule[(day, time)] = student_name


def assign_to_available_slot(schedule, student_timeslots, lesson_duration_in_quarter_hours, student_name):
    for day, timeslots in student_timeslots.items():
        for timeslot in timeslots:
            lesson_start_time = [time_plus(timeslot, timedelta(minutes=15 * i)) for i in range(lesson_duration_in_quarter_hours)]
            if is_slot_available(schedule, day, lesson_start_time):
                assign_student_to_slot(schedule, day, lesson_start_time, student_name)
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


def print_schedule(schedule):
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    timeslots = sorted(set(time for day, time in schedule.keys()), key=lambda x: [int(part) for part in x.split(':')])

    column_width = max(len(day) for day in days)
    column_width = max(column_width, max(len(str(schedule.get((day, time), ''))) for time in timeslots for day in days))

    # Print header
    print("Time   | " + " | ".join(day.ljust(column_width) for day in days))
    print("-" * (9 + 4 * len(days) + column_width * len(days)))

    # Print schedule
    for time in timeslots:
        row = [str(schedule.get((day, time), "")).ljust(column_width) for day in days]
        print(f"{time} | " + " | ".join(row))


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
    while best_schedule_match_percent < 100:
        shuffled_students = students.sample(frac=1).reset_index(drop=True)
        assign_students(shuffled_students, teachers)
        iteration += 1
        print(f' {iteration} iteration run. Current best match % is {best_schedule_match_percent}')
        if (datetime.now() - start_time).seconds >= duration:
            formatted_teacher_schedules = {teacher: {(day, time.strftime("%H:%M")): student for (day, time), student in timeslots.items()} for teacher, timeslots in best_schedule.items()}
            print(f'Student matched at {best_schedule_match_percent}%. Schedule: {formatted_teacher_schedules}')
            print(f'Unassigned students: {best_schedule_unassigned_students}')
            break

    for teacher, schedule in formatted_teacher_schedules.items():
        print(f"\n{teacher}'s Schedule:")
        print_schedule(schedule)

    print_schedule(formatted_teacher_schedules)
