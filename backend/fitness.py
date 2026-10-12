def calculate_fitness(schedule, subjects_data, preferred_times):

    score = 0
    subject_map = {s["name"]: s for s in subjects_data}

    all_slots = [e[0] for e in schedule]
    n_slots = len(all_slots)
    mid = n_slots // 2
    morning_slots = set(all_slots[:mid])
    evening_slots = set(all_slots[mid:])

    study_positions = [(i, slot, sub) for i, (slot, sub) in enumerate(schedule)
                       if sub != "Break"]
    n_study = len(study_positions)

    break_positions = []
    prev_subject = None

    for rank, (i, slot, subject) in enumerate(study_positions):
        data = subject_map.get(subject, {})
        priority   = data.get("priority", 1)    # 1=Low, 2=Med, 3=High
        difficulty = data.get("difficulty", 1)
        preferred  = preferred_times.get(subject, None)

      
        position_ratio = rank / max(n_study - 1, 1)

        if priority == 3:  # High priority
           
            if position_ratio < 0.33:
                score += 20
            elif position_ratio < 0.66:
                score += 5
            else:
                score -= 20   

        elif priority == 2:  # Medium priority
            if 0.25 <= position_ratio <= 0.75:
                score += 10
            else:
                score += 3

        else:  # Low priority
            if position_ratio > 0.6:
                score += 8
            elif position_ratio < 0.3:
                score -= 5  

        if preferred == "Morning" and slot in morning_slots:
            score += 8
        elif preferred == "Evening" and slot in evening_slots:
            score += 8
        elif preferred is not None:
            score -= 4  

        score += difficulty  

        if subject == prev_subject:
            score -= 15

        prev_subject = subject

    for i, (slot, sub) in enumerate(schedule):
        if sub == "Break":
            break_positions.append(i)
            if 0 < i < n_slots - 1:
                score += 5  

    present  = {s for _, s in schedule if s != "Break"}
    expected = {s["name"] for s in subjects_data}
    missing  = expected - present
    score -= len(missing) * 12
    if not missing:
        score += 20

    return score


def sort_schedule_by_priority(schedule, subjects_data):
   
    subject_map = {s["name"]: s for s in subjects_data}

    slots        = [e[0] for e in schedule]
    break_mask   = [e[1] == "Break" for e in schedule]
    study_subs   = [e[1] for e in schedule if e[1] != "Break"]

    
    study_subs_sorted = sorted(
        study_subs,
        key=lambda s: subject_map.get(s, {}).get("priority", 1),
        reverse=True
    )

    result = []
    sub_iter = iter(study_subs_sorted)
    for i, (slot, is_break) in enumerate(zip(slots, break_mask)):
        if is_break:
            result.append((slot, "Break"))
        else:
            result.append((slot, next(sub_iter)))

    return result