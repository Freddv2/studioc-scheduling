import csv
import re
from datetime import timedelta, datetime


def print_schedules(schedules):
    with open('schedules_visual.txt', 'w', encoding='utf-8') as file:
        print("\033[92m# Assigné au lieu et au professeur demandé\033[0m")
        print("\033[96m# Assigné au professeur mais pas au lieu\033[0m")
        print("\033[93m# Assigné au lieu mais pas au professeur\033[0m")
        print("\033[91m# Assigné ni au professeur ni au lieu demandé\033[0m")
        for teacher, schedule in schedules.items():
            teacher_schedule_title = f"\nHoraire de {teacher}:"
            print(teacher_schedule_title)
            schedule_output = print_teacher_schedule(schedule)
            print(schedule_output)  # Print to console
            file.write("\n" + teacher_schedule_title + "\n")
            file.write(re.sub(r'\033\[\d+m', '', schedule_output))  # Write to file without color codes


def print_teacher_schedule(schedule):
    availability_schedule = {}
    daily_instruments = {}
    daily_locations = {}

    for (day, time), entry in schedule.items():
        # Update availability_schedule
        if entry is not None:
            availability_schedule[(day, time)] = (entry['Name'], entry['preferred_teacher'], entry['preferred_location'])
            # Update daily_instruments and daily_locations
            if day not in daily_instruments or day not in daily_locations:
                daily_instruments[day] = entry['instrument']
                daily_locations[day] = entry['location']
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
        if day in daily_instruments:
            instrument = daily_instruments[day]
            location = daily_locations.get(day, "")
            teaching_days_header.append(f"{day.capitalize()} - {instrument}, {location}")

    # Handle the case where the teacher is not teaching
    if not teaching_days_header:
        for day in days_of_the_week:
            if any(d == day for d, _ in schedule.keys()):
                teaching_days_header.append(f"{day.capitalize()}")

    # Determine the column width based on the longest student name across the entire schedule
    column_width = max(len(str(value[0])) for value in availability_schedule.values())
    column_width = max(column_width, max(len(day) for day in teaching_days_header))  # Make sure the width is not smaller than day names

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
            cell, preferred_teacher, preferred_location = availability_schedule.get((day.lower(), time), (" " * column_width, None, None))
            cell = cell.center(column_width)
            color_code = determine_cell_color(preferred_teacher, preferred_location)
            formatted_cell = f"{color_code}{cell}\033[0m"
            row.append(formatted_cell)
        output.append(f"{time} | " + " | ".join(row))

    return "\n".join(output)


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

    nb_of_students_assigned_to_preferred_teacher = sum(1 for student in processed_students if student["Assigné à l'enseignant demandé"] is True)
    nb_of_students_asked_for_preferred_teacher = sum(1 for student in processed_students if student['Enseignant demandé'])
    percent_of_assigned_students_with_preferred_teacher = round((nb_of_students_assigned_to_preferred_teacher / nb_of_students_asked_for_preferred_teacher) * 100, 1)

    nb_of_assigned_students_with_ideal_timeslot = sum(1 for student in processed_students if student['Plage horaire idéale'] is True)
    percent_of_assigned_students_with_ideal_timeslot = round((nb_of_assigned_students_with_ideal_timeslot / len(processed_students)) * 100, 1)

    teachers_assignment_percentage = calculate_teachers_assignment_percentage(teacher_schedules)

    print(f'\nPreferred Teacher matched at {percent_of_assigned_students_with_preferred_teacher}%.')
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
