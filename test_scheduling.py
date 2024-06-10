from main import assign_students, run
import pandas as pd


# Sample test function
def test_siblings_scheduled_consecutively():
    students_data = {
        'student_name': ['Alice', 'Bob'],
        'instrument': ['piano', 'piano'],
        'location': ['patate', 'School'],
        'current_student': [True, False],
        'lesson_duration': ['45', '60'],
        'ideal_day': ['lundi', 'lundi'],
        'ideal_start_time': ['15:00', '15:15'],
        'ideal_end_time': ['17:00', '15:45'],
        'alternative_day_1': ['', ''],
        'alternative_start_time_1': ['', ''],
        'alternative_end_time_1': ['', ''],
        'alternative_day_2': ['', ''],
        'alternative_start_time_2': ['', ''],
        'alternative_end_time_2': ['', ''],
        'alternative_day_3': ['', ''],
        'alternative_start_time_3': ['', ''],
        'alternative_end_time_3': ['', ''],
        'simultaneous_family_class': [True, True],
        'sibling_name': ['Bob', 'Alice'],
        'age': [10, 12],
        'phone_number': ['123-456-7890', '123-456-7890'],
        'email': ['alice@example.com', 'bob@example.com'],
        'can_be_realocated': [True, True],
        'want_lesson': [True, True],
        'assigned_teacher': [pd.NA, pd.NA],
        'assigned_day': [pd.NA, pd.NA],
        'assigned_start_time': [pd.NA, pd.NA],
        'assigned_duration': [pd.NA, pd.NA],
        'preferred_teacher': ['Mr. Smith', 'Mr. Smith'],
    }

    teachers_data = {
        'teacher_name': ['Mr. Smith'],
        'instrument': ['piano, chant'],
        'location': ['School'],
        'day': ['lundi'],
        'start_time': ['14:00'],
        'end_time': ['18:00'],
        'start_break_1': [pd.NA],
        'end_break_1': [pd.NA],
        'length_break_1': [15],
        'accept_new_student': [True],
        'start_break_2': [pd.NA],
        'end_break_2': [pd.NA],
        'length_break_2': [pd.NA],
    }

    students = pd.DataFrame(students_data)
    teachers = pd.DataFrame(teachers_data)

    run(students,teachers)
