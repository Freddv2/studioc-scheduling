from datetime import timedelta, datetime
from itertools import groupby

def format_schedule(schedule):
    # Output dictionary
    new_schedule = {}

    # Iterate over each person in the original schedule
    for teacher, timeslots in schedule.items():
        # Sort the timeslots to ensure they are in the correct order
        sorted_timeslots = sorted(timeslots.items())

        # Group by the day and the student
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
            if teacher not in new_schedule:
                new_schedule[teacher] = {}
            new_schedule[teacher][new_key] = key[1]

    return new_schedule