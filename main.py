from datetime import timedelta, datetime
from itertools import groupby

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
        time = datetime.strptime(teacher['start_time'], '%H:%M').time()
        end_time = datetime.strptime(teacher['end_time'], '%H:%M').time()
        while time < end_time:
            schedule[teacher['teacher_name']][(teacher['day'], time)] = None
            time = time_plus(time, timedelta(minutes=15))
    return schedule

def format_schedule(schedule):
    # Output dictionary
    new_schedule = {}

    # Iterate over each person in the original schedule
    for person, timeslots in schedule.items():
        # Sort the timeslots to ensure they are in the correct order
        sorted_timeslots = sorted(timeslots.items())

        # Group by the day and the person
        for key, group in groupby(sorted_timeslots, lambda x: (x[0][0], x[1])):
            time_range = list(group)

            # If there are multiple timeslots in the group, combine them
            if len(time_range) > 1:
                start_time = time_range[0][0][1]
                end_time = (datetime.combine(datetime.today(), time_range[-1][0][1]) + timedelta(minutes=15)).time()
                new_key = (key[0], f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}")
            else:  # If there is only one timeslot, leave it as is
                new_key = (key[0], f"{time_range[0][0][1].strftime('%H:%M')}-{(datetime.combine(datetime.today(), time_range[0][0][1]) + timedelta(minutes=15)).time().strftime('%H:%M')}")

            # Add the timeslot(s) to the new schedule
            if person not in new_schedule:
                new_schedule[person] = {}
            new_schedule[person][new_key] = key[1]

    return new_schedule


def assign_students(students, teachers):
    teacher_schedules = create_schedule(teachers)
    students = students.sort_values(by='current_student', ascending=False)
    unassigned_students = []

    # Assign students to teachers
    for _, student in students.iterrows():
        for _, teacher in teachers.iterrows():
            current_schedule = teacher_schedules[teacher['teacher_name']]
            for timeslot in sorted(current_schedule.keys(), key=lambda x: str(x[1])):
                quarter_hour_increments = [time_plus(timeslot[1], timedelta(minutes=15 * i)) for i in range(student['lesson_duration'] // 15)]
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
            unassigned_students.append(student['student_name'])
    print(teacher_schedules)
    print(unassigned_students)
    formatted_schedule = format_schedule(teacher_schedules)
    print(formatted_schedule)
    return teacher_schedules, unassigned_students


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Read student data
    students = pd.read_csv('students.csv')
    # Read teacher data
    teachers = pd.read_csv('teachers.csv')
    teacher_schedules, unassigned_students = assign_students(students, teachers)
