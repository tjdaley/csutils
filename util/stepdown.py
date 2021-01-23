"""
stepdown.py - Produce a step-down schedule from a list of children.

Copyright (c) 2021 by Thomas J. Daley, J.D.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

STEPDOWN_MONTH = 6  # Assume children graduate high shcool in June
STEPDOWN_DAY = 30  # Last day before child support reduces is last day of month

def stepdown(children: list, initial_payment_amount: Decimal, num_children_not_before_court: int = 0) -> list:
    """
    Create a list of stepdown dates from a list of children.

    Each child in the children list must contain the following keys:
        * name (str) - The child's name
        * dob (datetime) - The child's date of birth
    The child can have other keys and they'll be returned to the caller.

    Each step-down date in the returned list will be a dict with these keys:
        * child (dict) - The dict provided by the caller re this this child
        * last_payment_date (datetime) - The date after which child support steps down
    
    Args:
        children (list): List of child dicts
        initial_payment_amount (Decimal): Amount of initial payment
        num_children_not_before_court (int): Number of children obligor is legally obligated
                                             to support who are not involved in this case.

    Returns:
        (list): List of dicts, one for each step down date. Values will be sorted
        by the stepdown_date attribute (ascending).
    
    Raises:
        ValueError: If a child is not properly constructed, i.e. missing
        a required key or having the wrong datatype as the value.
    """
    stepdown_dates = []
    initial_child_count = len(children)
    sorted_children = sorted(children, key=lambda k: k['dob'])

    while sorted_children:
        child = sorted_children.pop(0)
        __verify_child(child)
        turns_18 = child['dob'] + relativedelta(years=+18)
        if turns_18.month <= 6:
            stepdown_year = turns_18.year
        else:
            stepdown_year = turns_18.year + 1
        stepdown_date = datetime(stepdown_year, STEPDOWN_MONTH, STEPDOWN_DAY)
        stepdown_dates.append({
            'child': child,
            'last_payment_date': stepdown_date,
            'payment_amount': __stepdown_amount(initial_payment_amount, initial_child_count, len(sorted_children), num_children_not_before_court)
        })

    return sorted(stepdown_dates, key=lambda k: k['last_payment_date'])

REQUIRED_KEYS = [('name', str), ('dob', datetime)]
def __verify_child(child: dict) -> bool:
    for key_name, data_type in REQUIRED_KEYS:
        if key_name not in child:
            raise(ValueError(f"Invalid child. Missing key {key_name}"))
        if not isinstance(child[key_name], data_type):
            raise(ValueError(f"Invalid child. Value for '{key_name}'' must be {str(data_type)}"))
    return True

CHILD_SUPPORT_FACTORS = [
    [.2000, .2500, .3000, .3500, .4000, .4000, .4000],
    [.1750, .2250, .2738, .3220, .3733, .3771, .3800],
    [.1600, .2063, .2520, .3033, .3543, .3600, .3644],
    [.1475, .1900, .2400, .2900, .3400, .3467, .3520],
    [.1360, .1833, .2314, .2800, .3289, .3360, .3418],
    [.1333, .1786, .2250, .2722, .3200, .3273, .3333],
    [.1314, .1750, .2200, .2660, .3127, .3200, .3262],
    [.1300, .1722, .2160, .2609, .3067, .3138, .3200]
]
def __stepdown_amount(initial_payment_amount: Decimal, initial_child_count: int, remaining_child_count: int, num_children_not_before_court: int) -> Decimal:
    if num_children_not_before_court > len(CHILD_SUPPORT_FACTORS):
        row = len(CHILD_SUPPORT_FACTORS) - 1
    else:
        row = num_children_not_before_court
    factors = CHILD_SUPPORT_FACTORS[row]

    if remaining_child_count > len(factors):
        new_factor = factors[-1]
    else:
        new_factor = factors[remaining_child_count]

    if initial_child_count > len(factors):
        initial_factor = factors[-1]
    else:
        initial_factor = factors[initial_child_count-1]
    
    print("Initial   :", initial_payment_amount)
    print("Init count:", initial_child_count)
    print("Rem count :", remaining_child_count)
    print("Init factr:", initial_factor)
    print("New factor:", new_factor)

    net_resources = initial_payment_amount / Decimal(initial_factor)
    print("Net resour:", net_resources)
    new_amount = Decimal(net_resources * Decimal(new_factor))
    print("New amount:", new_amount)
    print("*" * 40)
    return round(new_amount, 2)
    


def test():
    test_children = [
        {'name': "Tom", 'dob': datetime(2015, 1, 29)},
        {'name': "Cindy", 'dob': datetime(2017, 5, 29)},
        {'name': "Ava", 'dob': datetime(2005, 9, 4)}
    ]
    print(stepdown(test_children, Decimal(1000)))

def test__verify_child():
    test_children = [
        ({}, False),
        ({'name': 15 }, False),
        ({'name': 'Tom'}, False),
        ({'name': 'Tom', 'dob': '1964-01-29'}, False),
        ({'name': 'Tom', 'dob': datetime(1964,1,29)}, True)
    ]

    for test_child, correct_result in test_children:
        try:
            if result := __verify_child(test_child):
                print("Good child:", test_child)
        except ValueError as e:
            result = False
            print(str(e))
        if result == correct_result:
            print("Passed")
        else:
            print("-----Failed")


test__verify_child()
test()