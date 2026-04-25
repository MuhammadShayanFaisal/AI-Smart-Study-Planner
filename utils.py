subjects = []
time_slots = []

def setup(subject_list, hours):
    global subjects, time_slots
    subjects = subject_list
    time_slots = [f"{9+i}-{10+i}" for i in range(hours)]