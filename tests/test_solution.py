## Student Name: Salim Haddad
## Student ID: 219930270

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
def test_meeting_too_long_for_workday_returns_empty():
    """
    Edge case:
    If meeting duration exceeds the available working window, return [].
    """
    events = []
    slots = suggest_slots(events, meeting_duration=24 * 60, day="2026-02-01")
    assert slots == []


def test_overlapping_events_are_merged_and_block_correctly():
    """
    Edge case:
    Overlapping events should be treated as one continuous busy interval.
    """
    events = [
        {"start": "10:00", "end": "11:00"},
        {"start": "10:30", "end": "12:00"},  # overlaps the first
    ]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    # Anything starting in the merged busy block should not be allowed
    assert "10:00" not in slots
    assert "10:15" not in slots
    assert "11:30" not in slots

    # A time after should be available (assuming still within work hours and not lunch rules)
    assert "13:00" in slots or "13:15" in slots



def test_event_partially_outside_working_hours_is_clipped():
    """
    Constraint:
    An event that overlaps working hours only partially should block the overlapping portion.
    """
    events = [{"start": "08:30", "end": "09:30"}]  # partially overlaps morning work start
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "09:00" not in slots
    assert "09:15" not in slots
    # After 09:30 should open up
    assert "09:45" in slots or "10:00" in slots


def test_event_touching_gap_boundary_blocks_start_time():
    """
    Edge case (boundary behavior):
    If a meeting ends exactly when an event starts, some specs treat that as conflict.
    This test checks the same boundary behavior implied by the public unsorted-events test.
    """
    events = [{"start": "09:30", "end": "10:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    # If end==event_start is considered conflict, 09:00 is NOT allowed (09:00-09:30 touches 09:30)
    assert "09:00" not in slots
    # 10:00 should be allowed after event ends
    assert "10:00" in slots


def test_slots_are_sorted_and_in_hhmm_format_and_reasonable_steps():
    """
    Sanity:
    Slots should be sorted ascending and formatted as HH:MM.
    Also checks that minutes look like typical increments (e.g., 15-min steps).
    """
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    # sorted ascending
    assert slots == sorted(slots)

    # format HH:MM and minutes in {00, 15, 30, 45} (common for these labs)
    for t in slots[:50]:  # sample first 50 so test is fast even if slots is long
        assert isinstance(t, str)
        assert len(t) == 5 and t[2] == ":"
        hh = int(t[:2])
        mm = int(t[3:])
        assert 0 <= hh <= 23
        assert mm in {0, 15, 30, 45}
