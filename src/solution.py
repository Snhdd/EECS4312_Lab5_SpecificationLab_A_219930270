## Student Name:Salim Haddad
## Student ID: 219930270

from typing import List, Dict, Tuple
from datetime import datetime

def suggest_slots(events: List[Dict[str, str]], meeting_duration: int, day: str) -> List[str]:
    if meeting_duration <= 0:
        return []

    def to_minutes(t: str) -> int:
        h, m = t.split(":")
        return int(h) * 60 + int(m)

    def to_hhmm(x: int) -> str:
        return f"{x // 60:02d}:{x % 60:02d}"

    WORK_START = to_minutes("09:00")
    WORK_END   = to_minutes("17:00")
    LUNCH_START = to_minutes("12:00")
    LUNCH_END   = to_minutes("13:00")
    STEP = 15

    # If meeting can't fit at all
    if WORK_START + meeting_duration > WORK_END:
        return []

    busy: List[Tuple[int, int]] = []

    # Add events clipped to working hours
    for e in events or []:
        if not isinstance(e, dict) or "start" not in e or "end" not in e:
            continue
        try:
            s = to_minutes(e["start"])
            en = to_minutes(e["end"])
        except Exception:
            continue
        if en <= s:
            continue

        # Ignore events completely outside working hours
        if en <= WORK_START or s >= WORK_END:
            continue

        s = max(s, WORK_START)
        en = min(en, WORK_END)
        if en > s:
            busy.append((s, en))

    # Lunch blocks time (treat like busy)
    busy.append((LUNCH_START, LUNCH_END))

    # Merge busy intervals, including "touching" intervals (s <= prev_end)
    busy.sort()
    merged: List[Tuple[int, int]] = []
    for s, en in busy:
        if not merged or s > merged[-1][1]:
            merged.append((s, en))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], en))

    def is_conflict(start: int) -> bool:
        end = start + meeting_duration
        for bs, be in merged:
            # Conflict if meeting overlaps OR touches busy at the start (end == bs is conflict)
            if start < be and end >= bs:
                return True
        return False

    # Round up to STEP boundary
    def ceil_to_step(t: int) -> int:
        r = t % STEP
        return t if r == 0 else t + (STEP - r)

    # --- NEW REQUIREMENT: Friday meetings must not start after 15:00 ---
    def is_friday(date_str: str) -> bool:
        try:
            # day is expected like "2026-02-01"
            return datetime.strptime(date_str, "%Y-%m-%d").weekday() == 4  # Monday=0 ... Friday=4
        except Exception:
            # If day can't be parsed, don't apply the Friday restriction
            return False

    slots: List[str] = []
    t = ceil_to_step(WORK_START)
    latest = WORK_END - meeting_duration

    if is_friday(day):
        latest = min(latest, to_minutes("15:00"))  # 15:00 allowed, anything after excluded

    while t <= latest:
        if not is_conflict(t):
            slots.append(to_hhmm(t))
        t += STEP

    return slots
