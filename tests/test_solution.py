## Student Name: Ali Ashraf
## Student ID: 218990184

"""
Public test suite for the meeting slot suggestion exercise.

Students can run these tests locally to check basic correctness of their implementation.
The hidden test suite used for grading contains additional edge cases and will not be
available to students.
"""
import pytest
from solution import suggest_slots


def test_single_event_blocks_overlapping_slots():
    """
    Functional requirement:
    Slots overlapping an event must not be suggested.
    """
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "10:00" not in slots
    assert "10:30" not in slots
    assert "11:15" in slots

def test_event_outside_working_hours_is_ignored():
    """
    Constraint:
    Events completely outside working hours should not affect availability.
    """
    events = [{"start": "07:00", "end": "08:00"}]
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-01")

    assert "09:00" in slots
    assert "16:00" in slots

def test_unsorted_events_are_handled():
    """
    Constraint:
    Event order should not affect correctness.
    """
    events = [
        {"start": "13:00", "end": "14:00"},
        {"start": "09:30", "end": "10:00"},
        {"start": "11:00", "end": "12:00"},
    ]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert  slots[1] == "10:15"
    assert "09:30" not in slots

def test_lunch_break_blocks_all_slots_during_lunch():
    """
    Constraint:
    No meeting may start during the lunch break (12:00–13:00).
    """
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "12:00" not in slots
    assert "12:15" not in slots
    assert "12:30" not in slots
    assert "12:45" not in slots

"""TODO: Add at least 5 additional test cases to test your implementation."""
"""TODO: Add at least 5 additional test cases to test your implementation."""

def test_overlapping_events_are_merged():
    """
    Overlapping events should not create fake gaps.
    """
    events = [
        {"start": "09:30", "end": "10:30"},
        {"start": "10:00", "end": "11:00"},
    ]
    # Busy becomes 09:30–11:00 (+buffer => 11:15)
    slots = suggest_slots(events, meeting_duration=30, day="Tue")
    assert "10:15" not in slots
    assert "11:15" in slots


def test_back_to_back_events_block_continuously():
    """
    Adjacent events should behave like continuous busy time.
    """
    events = [
        {"start": "09:00", "end": "10:00"},
        {"start": "10:00", "end": "10:30"},
    ]
    # Busy becomes 09:00–10:30 (+buffer => 10:45)
    slots = suggest_slots(events, meeting_duration=15, day="Mon")
    assert "10:30" not in slots
    assert "10:45" in slots


def test_event_partially_outside_working_hours_is_clipped():
    """
    Events partly outside working hours should be clipped, not ignored.
    """
    events = [{"start": "08:00", "end": "09:30"}]
    # Clipped to 09:00–09:30 (+buffer => 09:45)
    slots = suggest_slots(events, meeting_duration=30, day="Wed")
    assert "09:00" not in slots
    assert "09:45" in slots


def test_meeting_can_end_exactly_at_work_end():
    """
    A meeting that ends exactly at 17:00 should be allowed.
    """
    slots = suggest_slots([], meeting_duration=60, day="Thu")
    assert "16:00" in slots
    assert "16:15" not in slots  # would end at 17:15


def test_duration_too_long_returns_empty():
    """
    Duration longer than the whole workday should return no slots.
    """
    slots = suggest_slots([], meeting_duration=8 * 60 + 1, day="Fri")
    assert slots == []
#addition of new requirement testing 
def test_friday_blocks_starts_after_1500():
    """
    On Friday, meetings must not start after 15:00.
    15:00 is allowed, but 15:15 and later are excluded.
    """
    slots = suggest_slots([], meeting_duration=30, day="Fri")

    assert "15:00" in slots
    assert "15:15" not in slots
    assert "16:00" not in slots
    
def test_non_friday_allows_starts_after_1500():
    """
    On non-Friday days, meetings may start after 15:00
    as long as they fit within working hours.
    """
    slots = suggest_slots([], meeting_duration=30, day="Thu")

    assert "15:15" in slots
    assert "16:00" in slots

