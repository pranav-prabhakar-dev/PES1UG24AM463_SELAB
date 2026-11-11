"""Lab 6: Code (line) coverage test cases for visa_application.py

Name: Pranav Prabhakar
SRN:  PES1UG24AM463
Class: 5-H

Goal: execute every line of visa_application.py at least once.
Run:  coverage run --source=visa_application -m pytest CodeCoverageTest_PES1UG24AM463_application.py
      coverage report -m
"""

import pytest

from visa_application import visa_fee, documents_complete, application_status


# ---------------------------------------------------------------- visa_fee

def test_unknown_visa_type_raises():
    """Executes the guard clause and its raise."""
    with pytest.raises(ValueError, match="unknown visa type"):
        visa_fee("diplomatic", 1, "normal", "B")


def test_negative_entries_raises():
    """Executes the second guard clause and its raise."""
    with pytest.raises(ValueError, match="invalid entries"):
        visa_fee("tourist", -1, "normal", "B")


def test_entries_within_allowance_is_free():
    """tourist includes 1 entry, so 1 entry costs nothing."""
    assert visa_fee("tourist", 1, "normal", "B") == 0


def test_group_a_gets_an_extra_included_entry():
    """Group A adds 1 to the allowance, so included becomes 2 and 1 entry is billable."""
    assert visa_fee("tourist", 3, "normal", "A") == 40


def test_student_does_not_get_the_group_a_bonus():
    """Group A is True but the visa type is student, so no bonus is applied."""
    assert visa_fee("student", 3, "normal", "A") == 40


def test_express_rate_below_surcharge_threshold():
    """business includes 3; 5 entries leaves 2 extra at the express rate of 100."""
    assert visa_fee("business", 5, "express", "B") == 200


def test_normal_rate_above_surcharge_threshold():
    """9 extra entries triggers the +20 surcharge on the normal rate of 40."""
    assert visa_fee("tourist", 10, "normal", "B") == 9 * 60


def test_express_rate_above_surcharge_threshold():
    """9 extra entries on express: 100 + 20 surcharge + 10 express surcharge."""
    assert visa_fee("tourist", 10, "express", "B") == 9 * 130


# ------------------------------------------------------- documents_complete

def test_renewal_needs_only_one_form():
    assert documents_complete(1, 0, True) is True


def test_new_application_rejected_when_photos_missing():
    assert documents_complete(3, 1, False) is False


def test_new_application_accepted_with_three_forms_and_two_photos():
    assert documents_complete(3, 2, False) is True


# ------------------------------------------------------- application_status

def test_status_open_for_express():
    """Express cutoff is 10 days."""
    assert application_status(20, True, False) == "open"


def test_status_closing_for_normal():
    """Normal cutoff is 30; 20 days falls into the 15 day closing window."""
    assert application_status(20, False, False) == "closing"


def test_status_closed_for_normal():
    assert application_status(5, False, False) == "closed"


def test_peak_season_raises_the_cutoff():
    """Peak season adds 15 days, so 35 days is no longer open on a normal visa."""
    assert application_status(35, False, True) == "closing"
