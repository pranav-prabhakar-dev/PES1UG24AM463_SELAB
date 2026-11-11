"""Visa application helpers, hardened against malformed input.

Name: Pranav Prabhakar
SRN:  PES1UG24AM463
Class: 5-H

Fuzzing with Hypothesis showed every function trusted its argument. Each one
called .split() on it and then int()/float() on the pieces, so a non string
argument raised AttributeError, a missing or repeated delimiter raised
ValueError on unpacking, and non numeric text raised ValueError on conversion.
payable_fee had a quieter fault: float() accepts "nan" and "inf", so a corrupt
fee passed straight through max(total, 0) and reached the caller.

Every function now returns None for input it cannot parse, and never raises.
"""

import math


def _split_exactly(text, separator, parts):
    """Return the stripped fields of text, or None if it is not a string
    or does not split into exactly the expected number of fields."""
    if not isinstance(text, str):
        return None
    fields = text.split(separator)
    if len(fields) != parts:
        return None
    return [f.strip() for f in fields]


def parse_application(text):
    """Parse "visa_type:entries" into (Visa Type, entries).

    Returns None if text is not a string, does not contain exactly one colon,
    has an empty visa type, or has an entry count that is not a whole number
    of zero or more.
    """
    fields = _split_exactly(text, ':', 2)
    if fields is None:
        return None
    visa, entries = fields
    if not visa:
        return None
    try:
        count = int(entries)
    except (ValueError, TypeError):
        return None
    if count < 0:
        return None
    return visa.title(), count


def processing_average(days_csv):
    """Average a comma separated list of processing days, rounded down.

    Returns None if days_csv is not a string, is empty, or holds any field
    that is not a whole number of zero or more.
    """
    if not isinstance(days_csv, str):
        return None
    fields = days_csv.split(',')
    values = []
    for field in fields:
        try:
            value = int(field.strip())
        except (ValueError, TypeError):
            return None
        if value < 0:
            return None
        values.append(value)
    if not values:
        return None
    return sum(values) // len(values)


def payable_fee(text):
    """Work out the payable fee from "fee|discount", tax included.

    Returns None if text is not a string, does not contain exactly one pipe,
    holds a value that is not a number, or holds a value that is negative or
    not finite. The nan and inf check matters because float() accepts both.
    """
    fields = _split_exactly(text, '|', 2)
    if fields is None:
        return None
    try:
        fee = float(fields[0])
        discount = float(fields[1])
    except (ValueError, TypeError):
        return None
    if not (math.isfinite(fee) and math.isfinite(discount)):
        return None
    if fee < 0 or discount < 0:
        return None
    total = fee * 1.18 - discount
    if not math.isfinite(total):
        return None
    return max(total, 0)


def _report(label, value):
    if value is None:
        print(f"{label}: invalid input, please check the format and try again")
    else:
        print(f"{label}: {value}")


def main():
    print("==== Running parse_application ====")
    user_input = input("Enter visa type:entries (e.g. tourist:2): ")
    _report("Visa Type and Entries", parse_application(user_input))

    print("\n==== Running processing_average ====")
    user_input = input("Enter processing days as CSV (e.g. 5,10,21): ")
    _report("Average Processing Days", processing_average(user_input))

    print("\n==== Running payable_fee ====")
    user_input = input("Enter fee|discount (e.g. 6000|500): ")
    _report("Payable Fee", payable_fee(user_input))


if __name__ == "__main__":
    main()
