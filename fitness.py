"""
Fitness Module - Soft Constraint Scoring
Evaluates how optimal a schedule is beyond just being valid.

Priority rule:
  High-priority subjects MUST appear in earlier slots.
  The fitness function heavily penalizes high-priority subjects
  appearing late, and rewards them appearing early.
"""


def calculate_fitness(schedule, subjects_data, preferred_times):
    """
    Compute fitness score based on soft constraints.

    Key soft constraints scored here:
      - HIGH priority subjects should appear in the FIRST slots (strong reward/penalty)
      - Difficult subjects in preferred time window (morning/evening)
      - Well-placed breaks
      - No missing subjects
      - Position-weighted scoring: earlier slot = bigger reward for high priority

    subjects_data: list of dicts {name, priority, difficulty, hours}
    preferred_times: dict {subject_name: 'Morning'|'Evening'}
    Returns integer fitness score.
    """
    score = 0
    subject_map = {s["name"]: s for s in subjects_data}

    # Classify time windows (first half = morning, second half = evening)
    all_slots = [e[0] for e in schedule]
    n_slots = len(all_slots)
    mid = n_slots // 2
    morning_slots = set(all_slots[:mid])
    evening_slots = set(all_slots[mid:])

    # Study-only indices (ignoring breaks) for position weighting
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

        # ── Position-based priority scoring ─────────────────────────────
        # rank 0 = first study slot, rank n_study-1 = last study slot
        # position_ratio: 0.0 = very early, 1.0 = very late
        position_ratio = rank / max(n_study - 1, 1)

        if priority == 3:  # High priority
            # Strong reward for early placement, strong penalty for late
            # Early (ratio<0.33): +20, Mid: +5, Late (ratio>0.66): -20
            if position_ratio < 0.33:
                score += 20
            elif position_ratio < 0.66:
                score += 5
            else:
                score -= 20   # HIGH priority subject placed too late → big penalty

        elif priority == 2:  # Medium priority
            # Reward middle slots, small penalty for first or last
            if 0.25 <= position_ratio <= 0.75:
                score += 10
            else:
                score += 3

        else:  # Low priority
            # Low priority subjects should come later
            if position_ratio > 0.6:
                score += 8
            elif position_ratio < 0.3:
                score -= 5   # Low priority in prime early slot → penalty

        # ── Preferred time window ────────────────────────────────────────
        if preferred == "Morning" and slot in morning_slots:
            score += 8
        elif preferred == "Evening" and slot in evening_slots:
            score += 8
        elif preferred is not None:
            score -= 4  # Wrong time window

        # ── Difficulty bonus (harder = more reward for any slot) ─────────
        score += difficulty  # 1–5 bonus per slot

        # ── Consecutive same subject penalty ─────────────────────────────
        if subject == prev_subject:
            score -= 15

        prev_subject = subject

    # ── Break placement reward ───────────────────────────────────────────
    for i, (slot, sub) in enumerate(schedule):
        if sub == "Break":
            break_positions.append(i)
            if 0 < i < n_slots - 1:
                score += 5  # well-placed break

    # ── All subjects present bonus ───────────────────────────────────────
    present  = {s for _, s in schedule if s != "Break"}
    expected = {s["name"] for s in subjects_data}
    missing  = expected - present
    score -= len(missing) * 12
    if not missing:
        score += 20

    return score


def sort_schedule_by_priority(schedule, subjects_data):
    """
    Post-process: reorder study blocks so high-priority subjects
    appear before medium, and medium before low — while keeping
    breaks in their original positions.

    This is applied AFTER GA finishes to guarantee priority ordering.
    """
    subject_map = {s["name"]: s for s in subjects_data}

    # Separate break positions from study positions
    slots        = [e[0] for e in schedule]
    break_mask   = [e[1] == "Break" for e in schedule]
    study_subs   = [e[1] for e in schedule if e[1] != "Break"]

    # Sort study subjects by priority descending (High=3 first, Low=1 last)
    # Stable sort preserves relative order within same priority
    study_subs_sorted = sorted(
        study_subs,
        key=lambda s: subject_map.get(s, {}).get("priority", 1),
        reverse=True
    )

    # Rebuild schedule: fill non-break slots with sorted subjects
    result = []
    sub_iter = iter(study_subs_sorted)
    for i, (slot, is_break) in enumerate(zip(slots, break_mask)):
        if is_break:
            result.append((slot, "Break"))
        else:
            result.append((slot, next(sub_iter)))

    return result