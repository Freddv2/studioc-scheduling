from main import assign_students
import pandas as pd


# Sample test function
def test_siblings_scheduled_consecutively():
    students_data = {
        'student_name': ['Alice', 'Bob'],
        'instrument': ['piano', 'piano'],
        'location': ['School', 'School'],
        'current_student': [False, False],
        'lesson_duration': ['30', '30'],
        'ideal_day': ['Monday', 'Monday'],
        'ideal_start_time': ['15:00', '15:00'],
        'ideal_end_time': ['17:00', '17:00'],
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
        'preferred_teacher': ['', ''],
    }

    teachers_data = {
        'teacher_name': ['Mr. Smith'],
        'instrument': ['piano'],
        'location': ['School'],
        'day': ['Monday'],
        'start_time': ['14:00'],
        'end_time': ['18:00'],
        'start_break_1': ['16:00'],
        'end_break_1': ['16:15'],
        'length_break_1': [15],
        'accept_new_student': [True],
        'start_break_2': [pd.NA],
        'end_break_2': [pd.NA],
        'length_break_2': [pd.NA],
    }

    # Convert mock data to DataFrame
    students = pd.DataFrame(students_data)
    teachers = pd.DataFrame(teachers_data)

    # Call the scheduling function
    teachers_schedule = assign_students(students, teachers)  # you might need to adjust this call

    # Check if siblings are scheduled one after another
    # This is just an example, you need to adjust it based on your actual data structure
    print(teachers_schedule)
