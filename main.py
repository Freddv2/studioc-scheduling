import argparse
import bisect
import math
from datetime import timedelta, datetime

import pandas as pd

from formatter import print_schedules, output_to_csv

best_schedule = {}
best_processed_students = {}
best_students_assignment_percentage = 0
best_teachers_assignment_percentage = 0


def assign_students(prioritized_students, teachers):
    teachers_schedule = create_schedule(teachers)
    prioritized_students = sort_students(prioritized_students)
    processed_students = []

    for _, student in prioritized_students.iterrows():
        if is_student_processed(processed_students, student):
            continue

        if not student['want_lesson']:
            add_to_process_students(processed_students, [student], False)
            continue

        sibling_name = student.get('sibling_name')
        if student['simultaneous_family_class'] and sibling_name:
            sibling_row = prioritized_students[prioritized_students['student_name'].str.lower() == sibling_name]
            if not sibling_row.empty:
                if process_sibling_students(student, sibling_row.iloc[0], teachers_schedule, processed_students):
                    continue

        process_single_student(student, teachers_schedule, processed_students)

    update_best_iteration(teachers_schedule, processed_students)


def possible_teachers(student, teachers):
    # Create a temporary list of teachers teaching the same instrument
    teachers_that_teach_instrument = [teacher for _, teacher in teachers.iterrows() if student['instrument'] in map(str.strip, teacher['instrument'].split(","))]

    # Sort the list so that preferred teachers come first
    teachers_that_teach_instrument.sort(key=lambda teacher: not student['preferred_teacher'] == teacher['teacher_name'])
    return teachers_that_teach_instrument


def sort_students(students):
    # Order of instruments priority
    instrument_order = ["Violon", "Piano", "Chant", "Guitare", "Ukulélé", "Batterie"]

    def instrument_priority(instrument):
        try:
            return instrument_order.index(instrument)
        except ValueError:
            return len(instrument_order)

    students['instrument_priority'] = students['instrument'].apply(instrument_priority)
    return students.sort_values(
        by=['simultaneous_family_class', 'current_student', 'instrument_priority'],
        ascending=[False, False, True]
    )


# Helper function to check if the student has been processed
def is_student_processed(processed_students, student):
    return any(p_student['name'] == student['student_name'] for p_student in processed_students)


def process_single_student(student, teachers_schedule, processed_students):
    assigned = False
    for teacher in possible_teachers(student, teachers):
        teacher_schedule = teachers_schedule[teacher['teacher_name']]
        if student_and_teacher_are_at_same_location(student, teacher):
            if assign_to_available_slot(teacher_schedule, create_student_availability_schedule(student), int(student['lesson_duration']) // 15, student, teacher):
                assigned = True
                break
    add_to_process_students(processed_students, [student], assigned)


def process_sibling_students(student, sibling, teachers_schedule, processed_students):
    if sibling['instrument'] == student['instrument']:
        return process_sibling_same_instrument(student, sibling, teachers_schedule, processed_students)
    else:
        return process_sibling_different_instruments(student, sibling, teachers_schedule, processed_students)


def process_sibling_same_instrument(student, sibling, teachers_schedule, processed_students):
    for teacher in possible_teachers(student, teachers):
        if student_and_teacher_are_at_same_location(student, teacher):
            teacher_schedule = teachers_schedule[teacher['teacher_name']]
            if assign_siblings_one_after_another(teacher_schedule, student, sibling):
                add_to_process_students(processed_students, [student, sibling], True)
                return True
    return False


def process_sibling_different_instruments(student, sibling, teachers_schedule, processed_students):
    for day, timeslots in create_student_availability_schedule(student).items():
        for timeslot in timeslots:
            lesson_start_time = [time_plus(timeslot, timedelta(minutes=15 * i)) for i in range(int(student['lesson_duration']) // 15)]

            # Consider both possibilities: sibling starts either 15 minutes before or after student's lesson
            sibling_start_times = [[time_plus(time, timedelta(minutes=15 * (i - 1))) for time in lesson_start_time] for i in range(3)]

            for sibling_start_time in sibling_start_times:
                for student_teacher in possible_teachers(student, teachers):
                    for sibling_teacher in possible_teachers(sibling, teachers):
                        if student_and_teacher_are_at_same_location(student, student_teacher) and student_and_teacher_are_at_same_location(sibling, sibling_teacher):
                            student_teacher_schedule = teachers_schedule[student_teacher['teacher_name']]
                            sibling_teacher_schedule = teachers_schedule[sibling_teacher['teacher_name']]

                            if is_slot_available(student_teacher_schedule, day, lesson_start_time) and is_slot_available(sibling_teacher_schedule, day, sibling_start_time):
                                assign_student_to_slot(student_teacher_schedule, day, lesson_start_time, student, student_teacher)
                                assign_student_to_slot(sibling_teacher_schedule, day, sibling_start_time, sibling, sibling_teacher)
                                add_to_process_students(processed_students, [student, sibling], True)
                                return True
    return False


def assign_siblings_one_after_another(teacher_schedule, student, sibling):
    for day, timeslots in create_student_availability_schedule(student).items():
        for timeslot in timeslots:
            lesson_start_time = [time_plus(timeslot, timedelta(minutes=15 * i)) for i in range(int(student['lesson_duration']) // 15)]
            sibling_start_time = [time_plus(time, timedelta(minutes=int(sibling['lesson_duration']) * 15)) for time in lesson_start_time]

            if is_slot_available(teacher_schedule, day, lesson_start_time) and is_slot_available(teacher_schedule, day, sibling_start_time):
                assign_student_to_slot(teacher_schedule, day, lesson_start_time, student, teacher_schedule['teacher_name'])
                assign_student_to_slot(teacher_schedule, day, sibling_start_time, sibling, teacher_schedule['teacher_name'])
                print(f'Siblings: {student["student_name"]} & {sibling["student_name"]} were assigned one after the other')
                return True
    return False


def student_and_teacher_are_at_same_location(student, teacher):
    return student['location'] == teacher['location'] or student['can_be_realocated']


def assign_sibling_at_the_same_time(teachers_schedule, student_schedule, lesson_duration_in_quarter_hours, student, sibling, teachers):
    possible_teachers_student = possible_teachers(student, teachers)
    possible_teachers_sibling = possible_teachers(sibling, teachers)

    for day, timeslots in student_schedule.items():
        for timeslot in timeslots:
            student_start_time = [time_plus(timeslot, timedelta(minutes=15 * i)) for i in range(lesson_duration_in_quarter_hours)]
            sibling_start_time_same = [time_plus(time, timedelta(minutes=0)) for time in student_start_time]
            sibling_start_time_before = [time_plus(time, timedelta(minutes=-15)) for time in student_start_time]
            sibling_start_time_after = [time_plus(time, timedelta(minutes=15)) for time in student_start_time]

            for student_teacher in possible_teachers_student:
                if student['location'] != student_teacher['location'] and not student['can_be_realocated']:
                    continue
                student_teacher_schedule = teachers_schedule[student_teacher['teacher_name']]
                for sibling_teacher in possible_teachers_sibling:
                    if sibling['location'] != sibling_teacher['location'] and not student['can_be_realocated']:
                        continue
                    sibling_teacher_schedule = teachers_schedule[sibling_teacher['teacher_name']]
                    for sibling_start_time in [sibling_start_time_same, sibling_start_time_before, sibling_start_time_after]:
                        if is_slot_available(student_teacher_schedule, day, student_start_time) and is_slot_available(sibling_teacher_schedule, day, sibling_start_time):
                            assign_student_to_slot(student_teacher_schedule, day, student_start_time, student, student_teacher)
                            assign_student_to_slot(sibling_teacher_schedule, day, sibling_start_time, sibling, sibling_teacher)
                            print(f'Siblings: {student["student_name"]} & {sibling["student_name"]} were assigned at the same time')
                            return True
    return False


def create_student_availability_schedule(student):
    schedule = {student['ideal_day']: create_time_slots(student['ideal_start_time'], student['ideal_end_time'])}
    add_to_schedule(schedule, student['alternative_day_1'], student['alternative_start_time_1'], student['alternative_end_time_1'])
    add_to_schedule(schedule, student['alternative_day_2'], student['alternative_start_time_2'], student['alternative_end_time_2'])
    add_to_schedule(schedule, student['alternative_day_3'], student['alternative_start_time_3'], student['alternative_end_time_3'])
    return schedule


def add_to_process_students(processed_students, students, assigned):
    for student in students:
        processed_students.append({'name': student['student_name'], 'email': student['email'], 'phone': student['phone_number'], 'lesson_duration': student['lesson_duration'], 'assigned': assigned})


def update_best_iteration(teachers_schedule, processed_students):
    nb_of_assigned_students = sum(1 for student in processed_students if student['assigned'] is True)
    percent_of_assigned_students = round((nb_of_assigned_students / len(processed_students)) * 100, 1)

    teachers_assignment_percentage = calculate_teachers_assignment_percentage(teachers_schedule)

    global best_students_assignment_percentage
    if percent_of_assigned_students > best_students_assignment_percentage:
        best_students_assignment_percentage = percent_of_assigned_students
        global best_schedule
        best_schedule = teachers_schedule
        global best_processed_students
        best_processed_students = processed_students
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


def is_slot_available(teacher_schedule, day, quarter_hour_increments):
    return all((day, time) in teacher_schedule and teacher_schedule[(day, time)] is None for time in quarter_hour_increments)


def assign_student_to_slot(teacher_schedule, day, quarter_hour_increments, student, teacher):
    for time in quarter_hour_increments:
        teacher_schedule[(day, time)] = {'Name': student['student_name'], 'preferred_teacher': True if pd.isna(student['preferred_teacher']) or student['preferred_teacher'] == teacher['teacher_name'] else False}


def assign_to_available_slot(teacher_schedule, student_timeslots, lesson_duration_in_quarter_hours, student, teacher):
    for day, timeslots in student_timeslots.items():
        for timeslot in timeslots:
            lesson_start_time = [time_plus(timeslot, timedelta(minutes=15 * i)) for i in range(lesson_duration_in_quarter_hours)]
            if is_slot_available(teacher_schedule, day, lesson_start_time) and teacher_can_still_take_breaks(teacher_schedule, teacher):
                assign_student_to_slot(teacher_schedule, day, lesson_start_time, student, teacher)
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


def is_during_break(time, start_break, end_break):
    return start_break <= time.strftime("%H:%M") < end_break


def teacher_can_still_take_breaks(teacher_schedule, teacher):
    return teacher_can_still_take_break(teacher_schedule, teacher['start_break_1'], teacher['end_break_1'], teacher['length_break_1']) and teacher_can_still_take_break(teacher_schedule, teacher['start_break_2'], teacher['end_break_2'],
                                                                                                                                                                        teacher['length_break_2'])


def teacher_can_still_take_break(teacher_schedule, start, end, length):
    if pd.isna(start) or pd.isna(end) or pd.isna(length):
        return True
    available_break_time = sum(1 for day, time in teacher_schedule if is_during_break(time, start, end) and teacher_schedule[(day, time)] is None)
    return available_break_time >= length


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
            print(f'Student matched at {best_students_assignment_percentage}%.')
            print(f'Teachers matched at {best_teachers_assignment_percentage}%.')
            print(f'Processed students {best_processed_students}')
            break

    print_schedules(schedule)
    output_to_csv(schedule, best_processed_students)
