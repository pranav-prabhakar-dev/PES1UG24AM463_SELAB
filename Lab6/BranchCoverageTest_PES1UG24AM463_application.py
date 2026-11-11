"""Lab 6: Branch coverage test cases for visa_application.py

Name: Pranav Prabhakar
SRN:  PES1UG24AM463
Class: 5-H

Line coverage only asks whether a line ran. Branch coverage asks whether every
decision evaluated both True and False. Each test below is paired with its
opposite so that no decision is left half tested.

Run:  coverage run --branch --source=visa_application -m pytest BranchCoverageTest_PES1UG24AM463_application.py
      coverage report -m
"""

import pytest

from visa_application import visa_fee, documents_complete, application_status


# ------------------------------------------------------------------------
# visa_fee decision 1: visa_type not in INCLUDED_ENTRIES
# ------------------------------------------------------------------------

def test_unknown_visa_type_true_branch():
    with pytest.raises(ValueError, match="unknown visa type"):
        visa_fee("diplomatic", 1, "normal", "B")


def test_known_visa_type_false_branch():
    assert visa_fee("tourist", 1, "normal", "B") == 0


# ------------------------------------------------------------------------
# visa_fee decision 2: entries < 0
# ------------------------------------------------------------------------

def test_negative_entries_true_branch():
    with pytest.raises(ValueError, match="invalid entries"):
        visa_fee("tourist", -1, "normal", "B")


def test_zero_entries_false_branch():
    """Zero is the boundary: not negative, so it passes the guard."""
    assert visa_fee("tourist", 0, "normal", "B") == 0


# ------------------------------------------------------------------------
# visa_fee decision 3: nationality_group == "A" and visa_type != "student"
# Both operands are exercised independently so neither can hide the other.
# ------------------------------------------------------------------------

def test_group_a_non_student_true_branch():
    """Both operands True, so the allowance rises from 1 to 2."""
    assert visa_fee("tourist", 3, "normal", "A") == 40


def test_group_b_false_on_first_operand():
    """Group B, so the allowance stays at 1 and 2 entries are billable."""
    assert visa_fee("tourist", 3, "normal", "B") == 80


def test_group_a_student_false_on_second_operand():
    """Group A but a student visa, so the bonus is withheld."""
    assert visa_fee("student", 3, "normal", "A") == 40


# ------------------------------------------------------------------------
# visa_fee decision 4: extra <= 0
# ------------------------------------------------------------------------

def test_no_billable_entries_true_branch():
    assert visa_fee("business", 3, "normal", "B") == 0


def test_billable_entries_false_branch():
    assert visa_fee("business", 4, "normal", "B") == 40


# ------------------------------------------------------------------------
# visa_fee decision 5: speed == "express"
# ------------------------------------------------------------------------

def test_express_speed_true_branch():
    assert visa_fee("business", 5, "express", "B") == 200


def test_normal_speed_false_branch():
    assert visa_fee("business", 5, "normal", "B") == 80


# ------------------------------------------------------------------------
# visa_fee decision 6: extra > 5, and decision 7: the nested speed check
# ------------------------------------------------------------------------

def test_surcharge_true_branch_with_express():
    """9 extra entries on express: 100 base + 20 bulk + 10 express."""
    assert visa_fee("tourist", 10, "express", "B") == 9 * 130


def test_surcharge_true_branch_with_normal():
    """Same bulk surcharge, but the nested express check is False: 40 + 20."""
    assert visa_fee("tourist", 10, "normal", "B") == 9 * 60


def test_surcharge_false_branch_at_boundary():
    """Exactly 5 extra entries does not trigger the surcharge."""
    assert visa_fee("tourist", 6, "normal", "B") == 5 * 40


# ------------------------------------------------------------------------
# documents_complete decision 1: is_renewal
# ------------------------------------------------------------------------

def test_renewal_true_branch_accepted():
    assert documents_complete(1, 0, True) is True


def test_renewal_true_branch_rejected():
    """Renewal path still fails with no forms at all."""
    assert documents_complete(0, 0, True) is False


def test_not_a_renewal_false_branch():
    assert documents_complete(3, 2, False) is True


# ------------------------------------------------------------------------
# documents_complete decision 2: photos < 2
# ------------------------------------------------------------------------

def test_too_few_photos_true_branch():
    assert documents_complete(3, 1, False) is False


def test_enough_photos_false_branch_but_too_few_forms():
    """Photos are fine, so the final form count decides, and 2 is not enough."""
    assert documents_complete(2, 2, False) is False


# ------------------------------------------------------------------------
# application_status decision 1: is_express
# ------------------------------------------------------------------------

def test_express_true_branch():
    assert application_status(20, True, False) == "open"


def test_not_express_false_branch():
    assert application_status(20, False, False) == "closing"


# ------------------------------------------------------------------------
# application_status decision 2: is_peak_season
# ------------------------------------------------------------------------

def test_peak_season_true_branch():
    """Peak season lifts the normal cutoff from 30 to 45."""
    assert application_status(35, False, True) == "closing"


def test_off_peak_false_branch():
    """The same 35 days is open once the peak season bump is removed."""
    assert application_status(35, False, False) == "open"


# ------------------------------------------------------------------------
# application_status decisions 3 and 4: the open / closing / closed ladder
# ------------------------------------------------------------------------

def test_days_at_cutoff_is_open_true_branch():
    """Boundary: exactly at the cutoff counts as open."""
    assert application_status(30, False, False) == "open"


def test_below_cutoff_but_inside_window_is_closing():
    """First decision False, second True."""
    assert application_status(15, False, False) == "closing"


def test_below_both_thresholds_is_closed():
    """Both decisions False, reaching the final return."""
    assert application_status(5, False, False) == "closed"
