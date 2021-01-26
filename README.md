# csutils

*Package of child support calculation utilities.*

This package contains utility functions for creating step-down schedules, payment schedules, and compliance exhibits.

## Requirements

Requires Python v. 3.9 or higher.

## Installation

```
pip install csutils
```

## Usage

### Data Structures

#### *CHILD*

A *child* is a Python dict with the following keys:
* name - (str) - The child's name
* dob - (datetime) - The child's date of birth

```
child = {
    'name': "Tom",
    'dob': datetime(1964, 1, 29)
}
```

### *CHILDREN*

When a function requires *children* as an argument, that function is expecting
a Python list containing one or more *child* dicts.

```
child = {'name': "Tom", 'dob': datetime(1964, 1, 29)}
children = [child]
```

### Functions

#### Create a Step-Down Schedule

*A step-down schedule is a list of dates on which the amount of child support due changes based on a child aging out of the child support system.*

```
from decimal import Decimal
from csutils import stepdown

stepdown_schedule = stepdown(
    children=children,
    initial_payment_amount=Decimal(1000.00),
    num_children_not_before_court=0
)
```

### Create a List of Payments Due

*A payment-due list lists each date on which a certain type of payment is due, e.g. regular child support, medical support, or dental support.*

The functions that create schedules consume a *stepdown schedule*. That is to say that after creating the payment schedule, the stepdown schedule will be empty.

```
from datetime import datetime
from decimal import Decimal
from csutils stepdown
from csutils import payment_schedule

payments_due = payment_schedule(
    initial_amount=Decimal(1000.00),
    n_per_year=12,  # Ignored, for now, but required
    start_date=datetime(2019, 5, 1),
    step_down_schedule=stepdown_schedule,
    description='Child support due'
)
```

When called like that, the child support payment will be adjusted as each child ages out. That's fine for regular child support. However, medical insurance and dental
insurance reimbursements don't change based on the number of children. In other words, the payment is fixed across time. To create a payments due schedule of that type,
there is an optional argument,*fixed_payment*, that you set to ```True``` like this:

```
from datetime import datetime
from decimal import Decimal
from csutils import stepdown
from csutils import payment_schedule

insurance_payments_due = payment_schedule(
    initial_amount=Decimal(350.00),
    n_per_year=12,  # Ignored, for now, but required
    start_date=datetime(2019, 5, 1),
    step_down_schedule=stepdown_schedule,
    description='Medical insurance reimbursement due',
    fixed_payment=True
)
```

### Create a Combined List of Regular Child Support, Medical Insurance, and Dental Insurance Payments Due

This is the function you want when you want to create a list of payments due. It combines a list of child support, medical support, and dental support payments,
as applicable, to create a single list of payments due.

```
from datetime import datetime
from decimal import Decimal
from csutils import combined_payment_schedule

start_date = datetime(2019, 5, 1)
cs_payment = Decimal(1000.00)
health_ins_payment = Decimal(350.00)
dental_ins_payment = Decimal(50.00)

payments_due = combined_payment_schedule(
    children=children,
    initial_child_support_payment=cs_payment,
    health_insurance_payment=health_ins_payment,
    dental_insurance_payment=dental_ins_payment,
    confirmed_arrearage=None,
    start_date=start_date,
    num_children_not_before_court=0
)
```

### Create a list of payments.

This function will take a block text where each line of text it a payment and parse it as tab-delimited data, such as that
which you get when you copy and paste from the AG's web site. Alternatively, it can read TSV from a file. It creates a list of dicts where
each dict in the list contains the following keys:
* type (str): Always "Z"
* date (datetime): Date the payment was made
* amount (Decimal): The amount that was paid
* remaining_amount (Decimal): The amount of the payment that has not been allocated. This is for down-stream applications.
* description (str): Always "Payment made"

```
from csutils import payments_made
tsv = '01/01/2021\t387.50\txxxxxxx\n02/01/2020\t387.50\txxxxxxx'
payments = payments_made(tsv)
print(payments)
>>>
[
    {type: 'Z', date: datetime(2021,1,1,0,0), amount: 387.50, remaining_amount: 387.50, description='Payment made'},
    {type: 'Z', date: datetime(2021,2,1,0,0), amount: 387.50, remaining_amount: 387.50, description='Payment made'},
]
```

### Create an Activity Report

This function creates a list of dicts where each dict is either a payment (type=Z) or a payment that was due (type=A). This can be used to create a compliance report
that shows the total amount of a child support arrearage.

```
# Assume you obtained payments_due and payments from the code above.

report = compliance_report(payments_due, payments)
for line in report:
    v = line.split(DELIMITER)
    print(
        str(v[0]).ljust(15, ' '),
        v[1].ljust(25, ' '),
        str(v[2]).rjust(15, ' '),
        str(v[3]).rjust(15, ' '),
        str(v[4])
    )
>>>
[...]
12/01/2020      Child support due                 $322.92
12/01/2020      Medical support due               $100.00
12/09/2020      Payment made                                      $206.00
12/22/2020      Payment made                                      $206.00
12/30/2020      Payment made                                      $103.00
01/01/2021      Child support due                 $322.92
01/01/2021      Medical support due               $100.00
01/12/2021      Payment made                                      $206.00
                TOTALS                          $4,652.12       $3,089.00 Arrearage: $1,563.12
```

### Create a report that shows how payments should be applied to payments due to spot violations.

This function will apply payments to specific payments that were due according to the rules in the Texas Family Code.

```
# Assume you obtained payments_due and payments from the code above.

report = enforcement_report(payments_due, payments)
for pay_record_item in report:
    if pay_record_item['type'] == 'Z':
        continue
    print(
        pay_record_item['date'].strftime('%m/%d/%Y'),
        pay_record_item['description'].ljust(20, ' '),
        locale.currency(pay_record_item['amount'], grouping=True).rjust(15, ' '),
        locale.currency(pay_record_item['remaining_amount'], grouping=True).rjust(15, ' '),
    )
    for payment in pay_record_item.get('payments', []):
        print(
            ' '*10,
            payment['date'].strftime('%m/%d/%Y'),
            locale.currency(payment['amount'], grouping=True).rjust(15, ' ')
        )
>>>
03/01/2020 Child support due            $322.92         $322.92
03/01/2020 Medical support due          $100.00         $100.00
04/01/2020 Child support due            $322.92         $322.92
04/01/2020 Medical support due          $100.00         $100.00
05/01/2020 Child support due            $322.92         $322.92
05/01/2020 Medical support due          $100.00         $100.00
06/01/2020 Child support due            $322.92          $77.44
           08/21/2020          $64.16
           10/27/2020         $124.16
           12/30/2020          $57.16
06/01/2020 Medical support due          $100.00           $0.00
           08/21/2020         $100.00
07/01/2020 Child support due            $322.92           $0.00
           08/21/2020         $322.92
07/01/2020 Medical support due          $100.00           $0.00
           08/21/2020         $100.00
08/01/2020 Child support due            $322.92           $0.00
           08/18/2020          $94.00
           08/21/2020         $228.92
[...]
```

### Create a list of violations to put in your enforcement petition

This function builds on the enforcement report to generate text suitable to include in pleadings.

```
report = enforcement_report(payments_due, payments)
indictments = violations(report)
for violation_number, indictment in enumerate(indictments):
    print(f"VIOLATION {violation_number+1}: {indictment}\n\n")
>>>
VIOLATION 1:  According to the terms of the Child Support Order, Obligor was required to pay $322.92 to Obligee on March 1, 2020. Obligor violated the Child Support Order by failing to pay the full amount of $322.92 on or before March 1, 2020. Obligor instead paid a total of $0.00, leaving $322.92 in arrears.

VIOLATION 2:  According to the terms of the Child Support Order, Obligor was required to pay $100.00 to Obligee on March 1, 2020. Obligor violated the Child Support Order by failing to pay the full amount of $100.00 on or before March 1, 2020. Obligor instead paid a total of $0.00, leaving $100.00 in arrears.

VIOLATION 3:  According to the terms of the Child Support Order, Obligor was required to pay $322.92 to Obligee on April 1, 2020. Obligor violated the Child Support Order by failing to pay the full amount of $322.92 on or before April 1, 2020. Obligor instead paid a total of $0.00, leaving $322.92 in arrears.

VIOLATION 4:  According to the terms of the Child Support Order, Obligor was required to pay $100.00 to Obligee on April 1, 2020. Obligor violated the Child Support Order by failing to pay the full amount of $100.00 on or before April 1, 2020. Obligor instead paid a total of $0.00, leaving $100.00 in arrears.

VIOLATION 5:  According to the terms of the Child Support Order, Obligor was required to pay $322.92 to Obligee on May 1, 2020. Obligor violated the Child Support Order by failing to pay the full amount of $322.92 on or before May 1, 2020. Obligor instead paid a total of $0.00, leaving $322.92 in arrears.

VIOLATION 6:  According to the terms of the Child Support Order, Obligor was required to pay $100.00 to Obligee on May 1, 2020. Obligor violated the Child Support Order by failing to pay the full amount of $100.00 on or before May 1, 2020. Obligor instead paid a total of $0.00, leaving $100.00 in arrears.

VIOLATION 7:  According to the terms of the Child Support Order, Obligor was required to pay $322.92 to Obligee on June 1, 2020. Obligor violated the Child Support Order by failing to pay the full amount of $322.92 on or before June 1, 2020. Obligor instead paid a total of $245.48, leaving $77.44 in arrears.

VIOLATION 8:  According to the terms of the Child Support Order, Obligor was required to pay $322.92 to Obligee on January 1, 2021. Obligor violated the Child Support Order by failing to pay the full amount of $322.92 on or before January 1, 2021. Obligor instead paid a total of $106.00, leaving $216.92 in arrears.
```

## Author

Thomas J. Daley, J.D. is an active family law litigation attorney practicing primarily in Collin County, Texas, a family law mediator, and software developer. My family law practice is limited to divorce, child custody, child support, enforcment, and modification suits. [Web Site](https://koonsfuller.com/attorneys/tom-daley/)