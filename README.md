# csutils

*Package of child support calculation utilities.*

This package contains utility functions for creating step-down schedules, payment schedules, and compliance exhibits.

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
from csutils.stepdown import stepdown

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
from csutils.stepdown import stepdown
from csutils.payment_schedule import payment_schedule

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
from csutils.stepdown import stepdown
from csutils.payment_schedule import payment_schedule

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
from csutils.combined_payment_schedule import combined_payment_schedule

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

## Author

Thomas J. Daley, J.D. is an active family law litigation attorney practicing primarily in Collin County, Texas, a family law mediator, and software developer. My family law practice is limited to divorce, child custody, child support, enforcment, and modification suits. [Web Site](https://koonsfuller.com/attorneys/tom-daley/)