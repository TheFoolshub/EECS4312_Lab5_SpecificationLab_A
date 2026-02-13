## Student Name: Ali Ashraf
## Student ID: 218990184

from typing import List, Dict, Tuple
from datetime import datetime

WORK_START = "09:00"
WORK_END = "17:00"
STEP_MINUTES = 15
POST_EVENT_BUFFER = 15  # key to matching "10:15" / "11:15" in public tests

LUNCH_START = "12:00"
LUNCH_END = "13:00"

FRIDAY_LATEST_START = "15:00"  # NEW: on Friday, no meeting may start after 15:00


def _to_minutes(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _to_hhmm(x: int) -> str:
    return f"{x // 60:02d}:{x % 60:02d}"


def _merge(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []
    intervals.sort()
    out = [intervals[0]]
    for s, e in intervals[1:]:
        ps, pe = out[-1]
        if s <= pe:  # overlap/adjacent
            out[-1] = (ps, max(pe, e))
        else:
            out.append((s, e))
    return out


def _is_friday(day: str) -> bool:
    """
    Supports:
      - "Fri" / "Friday" (case-insensitive)
      - ISO date "YYYY-MM-DD"
    If parsing fails, falls back to prefix check.
    """
    if not isinstance(day, str):
        return False

    d = day.strip()
    if not d:
        return False

    # ISO date format
    try:
        dt = datetime.strptime(d, "%Y-%m-%d")
        # Monday=0 ... Friday=4
        return dt.weekday() == 4
    except ValueError:
        pass

    # Text day abbreviation/name
    return d.lower().startswith("fri")


def suggest_slots(
    events: List[Dict[str, str]],
    meeting_duration: int,
    day: str
) -> List[str]:
    """
    Suggest possible meeting start times for a given day.

    Working hours: 09:00–17:00
    Candidate starts: every 15 minutes
    Constraints:
      - Meeting must not overlap any event (events are [start,end))
      - Events entirely outside working hours are ignored; partial ones are clipped
      - After an event ends, meeting cannot start until 15 minutes later (post-buffer)
      - No meeting may start during lunch (12:00–13:00)
      - NEW: On Fridays, meetings must not start after 15:00
    """
    if not isinstance(meeting_duration, int) or meeting_duration <= 0:
        return []

    day_start = _to_minutes(WORK_START)
    day_end = _to_minutes(WORK_END)

    if meeting_duration > (day_end - day_start):
        return []

    busy: List[Tuple[int, int]] = []
    for ev in events or []:
        s = _to_minutes(ev["start"])
        e = _to_minutes(ev["end"])
        if e <= s:
            continue

        if e <= day_start or s >= day_end:
            continue

        # clip to working hours
        s = max(s, day_start)
        e = min(e, day_end)

        e = min(e + POST_EVENT_BUFFER, day_end)

        if e > s:
            busy.append((s, e))

    busy = _merge(busy)

    lunch_s = _to_minutes(LUNCH_START)
    lunch_e = _to_minutes(LUNCH_END)

    is_fri = _is_friday(day)
    fri_latest_start = _to_minutes(FRIDAY_LATEST_START)

    def overlaps_busy(start: int) -> bool:
        end = start + meeting_duration

        # must fit in working hours
        if start < day_start or end > day_end:
            return True

        # overlap check against busy intervals
        for bs, be in busy:
            # half-open overlap: [start,end) intersects [bs,be)
            if start < be and end > bs:
                return True
        return False

    slots: List[str] = []
    t = day_start
    while t + meeting_duration <= day_end:
        # NEW Friday rule: cannot START after 15:00 (15:00 allowed)
        if is_fri and t > fri_latest_start:
            break  # times only increase, so we can stop early

        # lunch rule: cannot START during lunch
        if lunch_s <= t < lunch_e:
            t += STEP_MINUTES
            continue

        if not overlaps_busy(t):
            slots.append(_to_hhmm(t))

        t += STEP_MINUTES

    return slots
