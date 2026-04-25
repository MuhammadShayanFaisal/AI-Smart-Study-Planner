"""
Fitness Module - Soft Constraint Scoring
Evaluates how optimal a schedule is beyond just being valid.
"""


def calculate_fitness(schedule, subjects_data, preferred_times):
    """
    Compute fitness score based on soft constraints.

    subjects_data: list of dicts with keys: name, priority, difficulty, hours
    preferred_times: dict of {subject_name: 'Morning'|'Evening'}

    Returns integer fitness score.
    """
    score = 0
    subject_map = {s["name"]: s for s in subjects_data}

    morning_slots = set()
    evening_slots = set()

    # Classify morning/evening (first half = morning, second half = evening)
    all_slots = [entry[0] for entry in schedule]
    mid = len(all_slots) // 2
    morning_slots = set(all_slots[:mid])
    evening_slots = set(all_slots[mid:])

    # Track subject counts and positions
    subject_counts = {}
    break_positions = []
    prev_subject = None

    for i, (slot, subject) in enumerate(schedule):
        if subject == "Break":
            break_positions.append(i)
            prev_subject = None
            continue

        data = subject_map.get(subject, {})
        priority = data.get("priority", 1)   # 1=Low, 2=Med, 3=High
        difficulty = data.get("difficulty", 1)
        preferred = preferred_times.get(subject, None)

        subject_counts[subject] = subject_counts.get(subject, 0) + 1

        # +10 for high priority subjects (more study time = better)
        if priority == 3:
            score += 10
        elif priority == 2:
            score += 5

        # +8 for difficult subjects scheduled in preferred time
        if preferred == "Morning" and slot in morning_slots:
            score += 8
        elif preferred == "Evening" and slot in evening_slots:
            score += 8
        elif preferred is not None:
            score -= 3  # scheduled in wrong time

        # -10 for consecutive same subject (duplication penalty)
        if subject == prev_subject:
            score -= 10

        prev_subject = subject

    # +5 for each break that's well-placed (not at start/end)
    for pos in break_positions:
        if 0 < pos < len(schedule) - 1:
            score += 5

    # -8 for imbalance: subjects with 0 hours when they should have some
    subject_names_in_schedule = {s for _, s in schedule if s != "Break"}
    expected_subjects = {s["name"] for s in subjects_data}
    missing = expected_subjects - subject_names_in_schedule
    score -= len(missing) * 8

    # Bonus for covering all subjects
    if not missing:
        score += 15

    return score