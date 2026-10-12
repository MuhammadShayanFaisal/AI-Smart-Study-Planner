

import random
from copy import deepcopy



def check_no_overlap(schedule):
    slots = [entry[0] for entry in schedule]
    return len(slots) == len(set(slots))


def check_break_frequency(schedule, max_continuous=2):
    continuous = 0
    for _, subject in schedule:
        if subject == "Break":
            continuous = 0
        else:
            continuous += 1
            if continuous > max_continuous:
                return False
    return True


def check_no_consecutive_same(schedule):
    for i in range(1, len(schedule)):
        if schedule[i][1] == schedule[i-1][1] and schedule[i][1] != "Break":
            return False
    return True


def check_subject_hours(schedule, subject_hours):
    counts = {}
    for _, subject in schedule:
        if subject != "Break":
            counts[subject] = counts.get(subject, 0) + 1
    for subject, limit in subject_hours.items():
        if counts.get(subject, 0) > limit:
            return False
    return True


def check_total_hours(schedule, total_expected):
    study_slots = sum(1 for _, s in schedule if s != "Break")
    return study_slots <= total_expected


def check_all_subjects_present(schedule, subjects):
    present = {s for _, s in schedule if s != "Break"}
    return all(sub in present for sub in subjects)



def get_violations(schedule, subject_hours, subjects):
    violations = []

    if not check_no_overlap(schedule):
        violations.append("[X] Overlapping time slots detected")

    if not check_no_consecutive_same(schedule):
        pairs = []
        for i in range(1, len(schedule)):
            if schedule[i][1] == schedule[i-1][1] and schedule[i][1] != "Break":
                pairs.append(schedule[i][1])
        violations.append(f"[X] Consecutive same subject: {', '.join(set(pairs))}")

    if not check_break_frequency(schedule):
        violations.append("[X] Missing break after 2+ continuous study hours")

    if not check_subject_hours(schedule, subject_hours):
        violations.append("[X] Subject hour limits exceeded")

    if not check_all_subjects_present(schedule, subjects):
        missing = [s for s in subjects if s not in {sub for _, sub in schedule}]
        violations.append(f"[X] Subjects missing from schedule: {', '.join(missing)}")

    return violations


def is_valid(schedule, subject_hours, subjects):
    return (
        check_no_overlap(schedule)
        and check_no_consecutive_same(schedule)
        and check_break_frequency(schedule)
        and check_subject_hours(schedule, subject_hours)
        and check_all_subjects_present(schedule, subjects)
    )



def repair(schedule, subject_hours, subjects, time_slots, break_interval=2):
   
    fixed = deepcopy(schedule)

    seen_slots = set()
    deduped = []
    for entry in fixed:
        if entry[0] not in seen_slots:
            seen_slots.add(entry[0])
            deduped.append(entry)
    fixed = deduped

    with_breaks = []
    continuous = 0
    for slot, subject in fixed:
        if subject == "Break":
            continuous = 0
            with_breaks.append((slot, subject))
        else:
            with_breaks.append((slot, subject))
            continuous += 1
            if continuous >= break_interval:
                continuous = 0

    fixed = with_breaks

    for i in range(1, len(fixed) - 1):
        if fixed[i][1] == fixed[i-1][1] and fixed[i][1] != "Break":
            if fixed[i+1][1] != fixed[i][1]:
                fixed[i], fixed[i+1] = (fixed[i][0], fixed[i+1][1]), (fixed[i+1][0], fixed[i][1])

    present = {s for _, s in fixed if s != "Break"}
    missing = [s for s in subjects if s not in present]
    for subject in missing:
        subject_counts = {}
        for idx, (slot, sub) in enumerate(fixed):
            if sub != "Break":
                subject_counts.setdefault(sub, []).append(idx)
        for sub, idxs in subject_counts.items():
            if len(idxs) > 1:
                replace_idx = idxs[-1]
                fixed[replace_idx] = (fixed[replace_idx][0], subject)
                break

    return fixed