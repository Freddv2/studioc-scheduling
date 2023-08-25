import csv
from datetime import timedelta, datetime


def print_schedules(schedule):
    for teacher, schedule in schedule.items():
        print(f"\n{teacher}'s Schedule:")
        print_teacher_schedule(schedule)


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

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    timeslots = sorted(set(time for day, time in availability_schedule.keys()), key=lambda x: [int(part) for part in x.split(':')])

    # Determine the column width based on the longest student name across the entire schedule
    column_width = max(len(str(value[0])) for value in availability_schedule.values())
    column_width = max(column_width, max(len(day) for day in days))  # Make sure the width is not smaller than day names

    # Print header
    print("Time   | " + " | ".join(day.ljust(column_width) for day in days))
    print("-" * (9 + 4 * len(days) + column_width * len(days)))

    # Print schedule
    for time in timeslots:
        row = []
        for day in days:
            cell, preferred_teacher = availability_schedule.get((day.lower(), time), (" " * column_width, None))
            cell = cell.center(column_width)  # Center the text within the column
            if preferred_teacher is None:
                color_code = "\033[91m" if cell.strip() == "(Available)" else "\033[0m"
            elif preferred_teacher:
                color_code = "\033[92m"
            else:
                color_code = "\033[93m"
            row.append(f"{color_code}{cell}\033[0m")
        print(f"{time} | " + " | ".join(row))


def output_to_csv(students):
    headers = students[0].keys()
    with open('schedule.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        # Write the header
        writer.writeheader()
        # Write the rows
        writer.writerows(students)
