import csv
import re
from datetime import timedelta, datetime


def print_schedules(teachers, schedules):
    with open('schedules_visual.txt', 'w', encoding='utf-8') as file:
        print("\033[92m# Assigné au lieu et au professeur demandé\033[0m")
        print("\033[96m# Assigné au professeur mais pas au lieu\033[0m")
        print("\033[93m# Assigné au lieu mais pas au professeur\033[0m")
        print("\033[91m# Assigné ni au professeur ni au lieu demandé\033[0m")
        for teacher, schedule in schedules.items():
            teacher_instrument = get_teacher_instrument(teachers, teacher)
            teacher_schedule_title = f"\nHoraire de {teacher} ({teacher_instrument})"
            print(teacher_schedule_title)
            schedule_output = print_teacher_schedule(teacher, teachers, schedule)
            print(schedule_output)  # Print to console
            file.write("\n" + teacher_schedule_title + "\n")
            file.write(re.sub(r'\033\[\d+m', '', schedule_output))  # Write to file without color codes


def print_teacher_schedule(teacher, teachers, schedule):
    availability_schedule = {}

    for (day, time), entry in schedule.items():
        # Update availability_schedule
        if entry is not None:
            availability_schedule[(day, time)] = (
                entry['Name'], entry['preferred_teacher'], entry['preferred_location'])
        else:
            availability_schedule[(day, time)] = ("(Disponible)", None, None)

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

    # Prepare the day headers with instrument and location
    days_of_the_week = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    teaching_days_header = []
    for day in days_of_the_week:
        teacher_row = get_teacher_by_day(teachers, teacher, day)
        if not teacher_row.empty:
            teaching_days_header.append(
                f"{day.capitalize()} - {teacher_row['location'].iloc[0]}")

    # Handle the case where the teacher is not teaching
    if not teaching_days_header:
        for day in days_of_the_week:
            if any(d == day for d, _ in schedule.keys()):
                teaching_days_header.append(f"{day.capitalize()}")

    # Determine the column width based on the longest student name across the entire schedule
    column_width = max(len(str(value[0])) for value in availability_schedule.values())
    column_width = max(column_width, max(
        len(day) for day in teaching_days_header))  # Make sure the width is not smaller than day names

    output = []
    # Print header
    header = "Heure  | " + " | ".join(day.ljust(column_width) for day in teaching_days_header)
    output.append(header)
    output.append("-" * (9 + 4 * len(teaching_days_header) + column_width * len(teaching_days_header)))

    # Print schedule
    for time in timeslots:
        row = []
        for day_header in teaching_days_header:
            day = day_header.split(' - ')[0].lower()
            cell, preferred_teacher, preferred_location = availability_schedule.get((day.lower(), time),
                                                                                    (" " * column_width, None, None))
            cell = cell.center(column_width)
            color_code = determine_cell_color(preferred_teacher, preferred_location)
            formatted_cell = f"{color_code}{cell}\033[0m"
            row.append(formatted_cell)
        output.append(f"{time} | " + " | ".join(row))

    return "\n".join(output)


def get_teacher_by_day(teachers_schedule, teacher_name, day):
    return teachers_schedule[(teachers_schedule['teacher_name'] == teacher_name) & (teachers_schedule['day'] == day)]


def get_teacher_instrument(teachers_schedule, teacher_name):
    teacher_rows = teachers_schedule[(teachers_schedule['teacher_name'] == teacher_name)]
    return teacher_rows['instrument'].iloc[0]


def determine_cell_color(preferred_teacher, preferred_location):
    color_code = "\033[0m"  # Default no color
    if preferred_teacher is None and preferred_location is None:
        return color_code
    elif preferred_teacher and preferred_location:
        color_code = "\033[92m"  # Green
    elif preferred_teacher and not preferred_location:
        color_code = "\033[96m"  # Cyan
    elif not preferred_teacher and preferred_location:
        color_code = "\033[93m"  # Yellow
    elif not preferred_teacher and not preferred_location:
        color_code = "\033[91m"
    return color_code


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

    print(f'\nStudent matched at {percent_of_assigned_students}%.')


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
