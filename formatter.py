import csv
import re
from datetime import timedelta, datetime


def print_schedules(schedules):
    with open('schedules_visual.txt', 'w', encoding='utf-8') as file:
        for teacher, schedule in schedules.items():
            teacher_schedule_title = f"\n{teacher}'s Schedule:"
            print(teacher_schedule_title)
            schedule_output = print_teacher_schedule(schedule)
            print(schedule_output)  # Print to console
            file.write("\n" + teacher_schedule_title + "àn\n")
            file.write(re.sub(r'\033\[\d+m', '', schedule_output))  # Write to file without color codes


def print_teacher_schedule(schedule):
    availability_schedule = {
        (day, time): (student['Name'], student['preferred_teacher']) if student is not None else ("(Available)", None)
        for (day, time), student in schedule.items()
    }

    # Determine the start and end times
    times = [time for day, time in schedule.keys()]
    start_time = datetime.strptime(min(times), "%H:%M")
    end_time = datetime.strptime(max(times), "%H:%M")

    # Generate all 15-minute timeslots between start and end times
    timeslots = []
    current_time = start_time
    while current_time <= end_time:
        timeslots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=15)

    # Filter days where the teacher is teaching
    teaching_days = [day for day in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
                     if any(day.lower() in key for key in availability_schedule.keys())]

    # Determine the column width based on the longest student name across the entire schedule
    column_width = max(len(str(value[0])) for value in availability_schedule.values())
    column_width = max(column_width, max(len(day) for day in teaching_days))  # Make sure the width is not smaller than day names

    output = []
    # Print header
    header = "Time   | " + " | ".join(day.ljust(column_width) for day in teaching_days)
    output.append(header)
    output.append("-" * (9 + 4 * len(teaching_days) + column_width * len(teaching_days)))

    # Print schedule
    for time in timeslots:
        row = []
        for day in teaching_days:
            cell, preferred_teacher = availability_schedule.get((day.lower(), time), (" " * column_width, None))
            cell = cell.center(column_width)  # Center the text within the column
            color_code = "\033[0m"  # Default no color
            if preferred_teacher is not None:
                color_code = "\033[92m" if preferred_teacher else "\033[93m"
            elif cell.strip() == "(Available)":
                color_code = "\033[91m"
            formatted_cell = f"{color_code}{cell}\033[0m"
            row.append(formatted_cell)
        output.append(f"{time} | " + " | ".join(row))

    return "\n".join(output)


def output_to_csv(students):
    headers = students[0].keys()
    with open('schedule.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        # Write the header
        writer.writeheader()
        # Write the rows
        writer.writerows(students)


def print_stats(processed_students, teacher_schedules):
    nb_of_assigned_students = sum(1 for student in processed_students if student['Assigné'] is True)
    percent_of_assigned_students = round((nb_of_assigned_students / len(processed_students)) * 100, 1)

    nb_of_students_assigned_to_preferred_teacher = sum(1 for student in processed_students if student["Assigné à l'enseignant demandé"] is True)
    nb_of_students_asked_for_preferred_teacher = sum(1 for student in processed_students if student['Enseignant demandé'])
    percent_of_assigned_students_with_preferred_teacher = round((nb_of_students_assigned_to_preferred_teacher / nb_of_students_asked_for_preferred_teacher) * 100, 1)

    nb_of_assigned_students_with_ideal_timeslot = sum(1 for student in processed_students if student['Plage horaire idéale'] is True)
    percent_of_assigned_students_with_ideal_timeslot = round((nb_of_assigned_students_with_ideal_timeslot / len(processed_students)) * 100, 1)

    teachers_assignment_percentage = calculate_teachers_assignment_percentage(teacher_schedules)

    print(f'Preferred Teacher matched at {percent_of_assigned_students_with_preferred_teacher}%.')
    print(f'Preferred Time Slot matched at {percent_of_assigned_students_with_ideal_timeslot}%.')
    print(f'Student matched at {percent_of_assigned_students}%.')
    print(f'Teachers matched at {teachers_assignment_percentage}%.')


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
