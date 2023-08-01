from datetime import timedelta, datetime
from typing import List, Dict

import pandas as pd

def create_timeslots(start_time, end_time, lesson_duration):
    start_time = datetime.strptime(start_time, '%H:%M:%S').time()
    end_time = datetime.strptime(end_time, '%H:%M:%S').time()
    lesson_duration = timedelta(minutes=lesson_duration)
    timeslots = []

    current_time = datetime.combine(datetime.today(), start_time)
    end_time = datetime.combine(datetime.today(), end_time)

    while current_time + lesson_duration <= end_time:
        timeslots.append(current_time.time())
        current_time += lesson_duration

    return timeslots


def time_plus(time, minutes):
    start = datetime(
        2000, 1, 1,  # dummy date
        hour=time.hour, minute=time.minute, second=time.second
    )
    end = start + minutes
    return end.time()

def create_schedule(teachers):
    schedule = {}
    for _,teacher in teachers.iterrows():
        schedule[teacher['teacher_name']] = {}
        for day in teacher['day']:
            time = datetime.strptime(teacher['start_time'], '%H:%M').time()
            end_time = datetime.strptime(teacher['end_time'], '%H:%M').time()
            while time < end_time:
                schedule[teacher['teacher_name']][(day, time)] = None
                time = time_plus(time, timedelta(minutes=15))
    return schedule

def format_final_teacher_schedule(teacher_schedules):
    # Combine consecutive slots
    for teacher in teacher_schedules:
        current_schedule = teacher_schedules[teacher]
        new_schedule = {}
        keys = sorted(current_schedule.keys(), key=lambda x: str(x[1]))
        i = 0
        while i < len(keys):
            start_time = keys[i]
            end_time = start_time
            student_name = current_schedule[start_time]
            while i + 1 < len(keys) and keys[i+1][0] == start_time[0] and current_schedule[keys[i+1]] == student_name and time_plus(end_time[1], timedelta(minutes=15)).strftime('%H:%M') == keys[i+1][1]:
                end_time = keys[i+1]
                i += 1
            new_key = (start_time[0], f"{start_time[1]}-{time_plus(end_time[1], timedelta(minutes=15)).strftime('%H:%M')}")
            new_schedule[new_key] = student_name
            i += 1
        teacher_schedules[teacher] = new_schedule


def assign_students(students, teachers):
    teacher_schedules = create_schedule(teachers)
    students = students.sort_values(by='current_student', ascending=False)
    unassigned_students = []

    # Assign students to teachers
    for _, student in students.iterrows():
        for _, teacher in teachers.iterrows():
            current_schedule = teacher_schedules[teacher['teacher_name']]
            for timeslot in sorted(current_schedule.keys(), key=lambda x: str(x[1])):
                quarter_hour_increments = [time_plus(timeslot[1], timedelta(minutes=15 * i)).strftime('%H:%M') for i in range(student['lesson_duration'] // 15)]
                is_slot_available = all(current_schedule.get((teacher['day'], time), None) is None for time in quarter_hour_increments)
                if is_slot_available:
                    # Assign the student to the teacher at the specified timeslot
                    for time in quarter_hour_increments:
                        current_schedule[(teacher['day'], time)] = student['student_name']
                    break
            else:
                continue
            break
        else:
            unassigned_students.append(student)
    format_final_teacher_schedule(teacher_schedules)
    return teacher_schedules,unassigned_students


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Read student data
    students = pd.read_csv('students.csv')
    # Read teacher data
    teachers = pd.read_csv('teachers.csv')
    teacher_schedules, unassigned_students = assign_students(students, teachers)
    print(teacher_schedules)
    print(unassigned_students)