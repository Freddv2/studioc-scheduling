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

    column_width = max(len(day) for day in days)
    column_width = max(column_width, len("\033[92m(Available)\033[0m"))
    column_width = max(column_width, max(len(str(value)) for value in availability_schedule.values()))

    # Print header
    print("Time   | " + " | ".join(day.ljust(column_width) for day in days))
    print("-" * (9 + 4 * len(days) + column_width * len(days)))

    # Print schedule
    for time in timeslots:
        row = []
        for day in days:
            cell, preferred_teacher = availability_schedule.get((day.lower(), time), ("-" * column_width, None))
            cell = cell.center(column_width).ljust(column_width)
            if preferred_teacher is None:
                color_code = "\033[91m" if cell.strip() == "(Available)" else "\033[0m"
            elif preferred_teacher:
                color_code = "\033[92m"
            else:
                color_code = "\033[93m"
            row.append(f"{color_code}{cell}\033[0m")
        print(f"{time} | " + " | ".join(row))


def output_to_csv(schedule):
    # Define the header
    header = ['Client', 'Professional', 'Durée', 'Jour', 'Time', 'Email', 'Téléphone']

    # Convert the data to a list of rows
    rows = []
    for teacher, lessons in schedule.items():
        student_lessons = {}
        for (day, time), lesson in lessons.items():
            if lesson is None:
                continue
            name = lesson['Name']
            email = lesson.get('email', '')
            phone = lesson.get('phone', '')
            duration = lesson.get('lesson_duration')
            if name not in student_lessons:
                student_lessons[name] = {
                    'Client': name,
                    'Professional': teacher,
                    'Durée': duration,
                    'Jour': day,
                    'Time': time,
                    'Email': email,
                    'Téléphone': phone
                }
        # Append the student lessons to the rows
        for student_lesson in student_lessons.values():
            rows.append(student_lesson)

    # Write to CSV file
    with open('schedule.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
