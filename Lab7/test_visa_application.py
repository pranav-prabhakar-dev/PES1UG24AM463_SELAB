"""Lab 7: Fuzz testing visa_application.py with Hypothesis

Name: Pranav Prabhakar
SRN:  PES1UG24AM463
Class: 5-H

Contract the hardened module is expected to honour:
  * No input, of any type, may raise. Unparseable input returns None.
  * Valid input still returns the correct value.

Run:  pytest test_visa_application.py
"""

import math

import pytest
from hypothesis import given, strategies as st

from visa_application import parse_application, processing_average, payable_fee


# ======================================================================
# Property 1: the functions must never crash, whatever they are handed.
# ======================================================================

@given(st.text() | st.none())
def test_parse_application_no_crash(s):
    try:
        parse_application(s)
    except Exception as e:
        assert False, f"parse_application crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_processing_average_no_crash(s):
    try:
        processing_average(s)
    except Exception as e:
        assert False, f"processing_average crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_payable_fee_no_crash(s):
    try:
        payable_fee(s)
    except Exception as e:
        assert False, f"payable_fee crashed with: {type(e).__name__}: {e}"


# ======================================================================
# Property 2: non string input must be rejected, not crash on .split()
# ======================================================================

@given(st.one_of(st.none(), st.integers(), st.floats(), st.booleans(),
                 st.lists(st.text()), st.dictionaries(st.text(), st.text())))
def test_non_string_input_is_rejected_cleanly(value):
    for fn in (parse_application, processing_average, payable_fee):
        try:
            assert fn(value) is None, f"{fn.__name__} accepted non string {value!r}"
        except Exception as e:
            assert False, f"{fn.__name__} crashed on {value!r}: {type(e).__name__}: {e}"


# ======================================================================
# Property 3: valid input must still produce the right answer.
# ======================================================================

@given(st.sampled_from(["tourist", "business", "student"]),
       st.integers(min_value=0, max_value=10 ** 6))
def test_parse_application_accepts_valid_input(visa, entries):
    assert parse_application(f"{visa}:{entries}") == (visa.title(), entries)


@given(st.lists(st.integers(min_value=0, max_value=10 ** 5),
                min_size=1, max_size=50))
def test_processing_average_matches_floor_mean(days):
    csv = ",".join(str(d) for d in days)
    assert processing_average(csv) == sum(days) // len(days)


@given(st.floats(min_value=0, max_value=10 ** 6,
                 allow_nan=False, allow_infinity=False),
       st.floats(min_value=0, max_value=10 ** 6,
                 allow_nan=False, allow_infinity=False))
def test_payable_fee_is_never_negative(fee, discount):
    result = payable_fee(f"{fee}|{discount}")
    assert result is not None, f"valid input rejected: {fee}|{discount}"
    assert result >= 0, f"negative fee returned: {result}"


# ======================================================================
# Property 4: specific edge cases found by fuzzing.
# ======================================================================

@pytest.mark.parametrize("bad", ["", "tourist", "a:b:c", "tourist:x", ":", "tourist:2.5"])
def test_parse_application_rejects_malformed(bad):
    assert parse_application(bad) is None


@pytest.mark.parametrize("bad", ["", "1,,3", "a,b", ","])
def test_processing_average_rejects_malformed(bad):
    assert processing_average(bad) is None


@pytest.mark.parametrize("bad", ["", "6000", "a|b", "6000|500|1"])
def test_payable_fee_rejects_malformed(bad):
    assert payable_fee(bad) is None


@pytest.mark.parametrize("bad", ["nan|0", "inf|0", "-inf|0", "1e400|0", "6000|nan"])
def test_payable_fee_rejects_non_finite_numbers(bad):
    """float() happily parses 'nan' and 'inf', so a corrupt fee can slip
    through max(total, 0) and reach the caller as nan or inf."""
    assert payable_fee(bad) is None


def test_payable_fee_result_is_always_finite():
    result = payable_fee("6000|500")
    assert result is not None and math.isfinite(result)
