# Leave Self-Service Administration Guide

This guide explains the Frappe HR administration prerequisites that must be in place for `frappe_hr_self_service` to work reliably.

It is intentionally generic. Organization-specific leave policy belongs in your own custom app or operational documentation.

Examples of policy that are **not** defined here include:

- exact leave entitlement quantities;
- waiting periods;
- leave-type sequencing or priority rules;
- carry-forward rules;
- encashment rules;
- organization-specific cutover decisions;
- branding, Workspace names, and employee-facing labels.

This guide does, however, explain how to configure the Frappe HR masters that express those choices: **Leave Types, Leave Periods, Leave Policies, Leave Policy Assignments, and Leave Allocations**.

For a worked example of building the employee-facing UI with a Frappe Workspace, Custom HTML Blocks, Web Pages, and these APIs, see:

[Employee Self-Service UI Starter Guide](EMPLOYEE_SELF_SERVICE_UI_STARTER_GUIDE.md)

Useful upstream Frappe HR documentation:

- [Leave Type](https://docs.frappe.io/hr/leave-type)
- [Leave Period](https://docs.frappe.io/hr/leave-period)
- [Leave Policy](https://docs.frappe.io/hr/leave-policy)
- [Leave Policy Assignment](https://docs.frappe.io/hr/leave-policy-assignment)
- [Leave Allocation](https://docs.frappe.io/hr/leave-allocation)

---

## 1. Purpose

`frappe_hr_self_service` provides a simplified employee and approver layer on top of Frappe HR leave workflows.

The public app does not replace Frappe HR's core documents or validation. Frappe HR remains the system of record for:

- Employees;
- Users;
- Leave Approvers;
- Holiday Lists;
- Leave Types;
- Leave Periods;
- Leave Policies;
- Leave Policy Assignments;
- Leave Allocations;
- Leave Applications;
- leave balances and ledger behavior;
- native submission and validation rules.

The purpose of this guide is to describe the administrative setup that must exist underneath the self-service experience.

A working self-service installation should allow an employee to:

- log in as their own Frappe user;
- see their leave balances;
- select dates and retrieve eligible leave types;
- submit a leave request;
- view their own leave requests;
- have the configured approver review and approve or reject the request;
- see the resulting leave balance reflect approved leave.

---

## 2. Important principle: saved is not the same as submitted

Many Frappe HR documents are not operational merely because they have been saved.

Where this guide says **Submit**, verify that the document actually shows a submitted state rather than Draft.

A common setup failure is:

```text
Document exists
    but
Document is still Draft
    therefore
Expected leave behavior does not occur
```

For leave setup, always verify document status after configuration.

---

## 3. Core documents and what "ready" means

A typical employee self-service setup depends on the following:

| Document / Setting | Ready state |
|---|---|
| Employee | Active, correct Company, correct Date of Joining |
| User | Enabled and linked to exactly one active Employee |
| Employee role/access | Appropriate employee access is present |
| Employee self-service home | User can reach the organization's employee self-service UI |
| Leave Approver | Set on the Employee |
| Holiday List Assignment | Correct dates and Submitted |
| Leave Type | Configured to express the intended leave behavior |
| Leave Period | Correct allocation period, when your organization uses Leave Periods |
| Leave Policy | Correct Leave Type rows and annual allocations; Submitted |
| Leave Policy Assignment | Submitted, when generating entitlement through policy |
| Leave Allocation | Submitted and valid for the relevant date range |
| Leave Application | Created and processed through the normal Frappe HR workflow |

The exact UI names and routes are organization-specific.

---

# Part I - Employee identity and access

## 4. Create or verify the Employee

Open the Employee record and confirm at least:

- Employee Name;
- Company;
- Status = Active;
- Date of Joining = the employee's actual date of joining;
- any other mandatory HR fields required by your installation.

### Verify

The Employee must show the correct Company and actual Date of Joining.

Do not replace the historical Date of Joining with an ERP rollout or migration date.

---

## 5. Create or verify the User

Create a Frappe User for the employee if one does not already exist.

Recommended minimum:

- User is enabled;
- the User has the employee access required by your installation;
- the User is not given HR Manager, System Manager, or other elevated roles unless those roles are genuinely required.

Then link the Employee to the User using the Employee's **User ID** field.

### Verify

Confirm:

- Employee.User ID is not blank;
- the User is enabled;
- exactly one active Employee is linked to that User.

The self-service APIs derive employee identity from the authenticated Frappe user. A clean one-user-to-one-active-employee relationship is therefore important.

---

## 6. Configure the employee self-service home

Your organization may use a Workspace such as `My HR`, `Employee Self Service`, or another name.

Set the user's default Workspace if you want the employee to land there after login.

### Verify

Test with the employee's own account, preferably in a fresh or incognito browser session.

The employee should be able to reach the self-service home without relying on Administrator or System Manager privileges.

For a generic UI pattern, see the [Employee Self-Service UI Starter Guide](EMPLOYEE_SELF_SERVICE_UI_STARTER_GUIDE.md).

---

# Part II - Approver setup

## 7. Set the Leave Approver

On the Employee record, set the appropriate Leave Approver according to your Frappe HR configuration.

The approver should be a valid, enabled Frappe User.

### Verify

Confirm:

- the Employee references the correct approver;
- the approver User exists and is enabled;
- the approver has the permissions or role required by your installation to process leave requests.

The self-service approver workflow still relies on Frappe HR's Leave Application and approval authority.

---

# Part III - Holiday setup

## 8. Configure the Holiday List Assignment

Create the Holiday List Assignment required for the employee and the dates your organization manages in Frappe HR.

A typical assignment includes:

- Applicable For = Employee;
- Employee = the employee being configured;
- Holiday List = the applicable calendar;
- Starts On = the appropriate effective date.

Save and **Submit** the assignment.

### Why this matters

Frappe HR needs the applicable holiday calendar when calculating leave days between the requested From Date and To Date.

It is possible for leave balances to display correctly while date-based eligibility fails because no applicable Holiday List can be found.

### Verify

Confirm:

- the assignment is Submitted;
- the requested leave dates fall within a period for which Frappe HR can resolve a Holiday List.

---

# Part IV - Leave Types, Leave Period, and Leave Policy

Before deciding how employee balances will be created, configure the leave masters that define the organization's leave scheme.

These records answer different questions:

```text
Leave Type
    What kind of leave is this and how should it behave?

Leave Period
    For what time window are leaves being managed?

Leave Policy
    How many days of each Leave Type is an employee entitled to for that period?

Leave Policy Assignment
    Which employee receives that policy for which period?

Leave Allocation
    What actual leave balance/allocation exists for that employee?
```

---

## 9. Create or review Leave Types

Create the Leave Types required by your organization before building a Leave Policy.

Examples might include:

```text
Casual Leave
Sick Leave
Privilege / Earned Leave
Leave Without Pay
Optional Leave
```

The exact names and rules are organization-specific.

Important Leave Type settings in Frappe HR include, depending on the type of leave:

- **Maximum Leave Allocation Allowed per Leave Period**;
- **Allow Leave Application After (Working Days)**;
- **Maximum Consecutive Leaves Allowed**;
- **Is Carry Forward**;
- **Is Leave Without Pay**;
- **Is Optional Leave**;
- **Allow Negative Balance**;
- **Allow Over Allocation**;
- **Include holidays within leaves as leaves**;
- **Allow Encashment**;
- **Is Earned Leave** and its earning frequency;
- partially paid leave settings, where applicable.

### Important distinction

A Leave Type defines the **behavior and constraints** of that category of leave.

It does not, by itself, give an employee a balance.

The employee receives usable entitlement through a Leave Allocation, commonly generated from a Leave Policy Assignment or created/imported directly.

### Earned Leave note

If a Leave Type is configured as **Earned Leave**, its balance may accrue over time according to the configured earning frequency instead of appearing as the full annual entitlement immediately.

That behavior should be understood before testing self-service balances.

### Verify

For every Leave Type, confirm that its configuration matches the organization's approved policy before using it in a Leave Policy.

---

## 10. Create or review the Leave Period

Many organizations manage leave on a calendar-year or fiscal-year basis.

Create the applicable Leave Period when your implementation uses one.

Typical fields include:

- Company;
- From Date;
- To Date;
- active status;
- optional-holiday configuration, when used.

For example:

```text
Calendar-year organization
From Date: 01-Jan-2027
To Date:   31-Dec-2027
```

or:

```text
Fiscal leave year
From Date: 01-Apr-2027
To Date:   31-Mar-2028
```

The start of the next **Leave Period**, rather than January 1 specifically, is the important boundary when moving employees onto a new annual policy.

---

## 11. Build and submit the Leave Policy

Create a Leave Policy that represents the organization's entitlement scheme.

For each applicable Leave Type, add a policy row with its **Annual Allocation**.

Example only:

| Leave Type | Annual Allocation |
|---|---:|
| Casual Leave | 10 |
| Sick Leave | 12 |
| Privilege Leave | 15 |

Do not copy these example quantities unless they match your organization's actual policy.

### Relationship between Leave Type and Leave Policy

Think of the two documents this way:

```text
Leave Type
    defines rules and behavior

Leave Policy
    groups selected Leave Types
    and defines annual entitlement quantities
```

The Leave Type's maximum-allocation settings can constrain what is valid in the Leave Policy.

After reviewing the policy rows, **Save and Submit** the Leave Policy.

### Verify

Confirm:

- every intended Leave Type is present;
- Annual Allocation is correct for each row;
- no unintended Leave Type is included;
- the Leave Policy is Submitted.

Submitting the Leave Policy itself does **not** create an employee's Leave Allocations. The policy still has to be assigned to an employee.

---

# Part V - Establish employee entitlement

There are two common administrative patterns.

They serve different purposes and should not normally be combined for the same employee and the same allocation period.

---

## 12. Pattern A - Generate entitlement from a Leave Policy Assignment

This is the normal **steady-state** pattern when Frappe HR is responsible for creating the employee's entitlement for the applicable Leave Period.

It is typically appropriate for:

- new employees after Frappe HR becomes the system of record;
- existing employees at the start of a new Leave Period;
- bulk annual leave allocation when the organization uses Leave Policies as its standard entitlement mechanism.

The flow is:

```text
Configured Leave Types
  ↓
Submitted Leave Policy
  ↓
Employee
  ↓
User + Employee linkage
  ↓
Leave Approver
  ↓
Holiday List Assignment
  ↓
Submitted Leave Policy Assignment
  ↓
Leave Allocations generated by Frappe HR
  ↓
Self-service verification
```

---

## 13. Create the Leave Policy Assignment

Create a Leave Policy Assignment for the employee.

Typical fields include:

- Employee;
- Leave Policy;
- Assignment Based On;
- Leave Period, when applicable;
- effective dates;
- any carry-forward option that your organization intentionally uses.

Frappe HR supports assignment based on a Leave Period, the employee's Joining Date, or manually defined effective dates.

Save the document, review it, and then **Submit** it.

On submission, Frappe HR creates Leave Allocation documents based on the assigned Leave Policy.

### Critical check

A Leave Policy Assignment left in Draft may not generate usable employee Leave Allocations.

### Verify

Confirm:

- status = Submitted;
- employee is correct;
- Leave Policy is correct;
- Leave Period or effective dates are correct.

---

## 14. Verify generated Leave Allocations

After the Leave Policy Assignment is submitted, verify the allocations Frappe HR generated.

For each expected Leave Type, check:

- correct Employee;
- correct Leave Type;
- expected allocation quantity according to your policy;
- correct date range;
- Leave Policy Assignment reference is populated;
- status = Submitted;
- earned-leave schedules behave as expected if the Leave Type is configured as earned leave.

`frappe_hr_self_service` reads the resulting Frappe HR leave state; it does not replace the entitlement-generation process.

---

## 15. Pattern B - Import existing opening balances during cutover

Pattern B is normally the **recommended cutover pattern for employees who already exist when Frappe HR is introduced partway through an active Leave Period**, provided HR has an authoritative remaining balance for those employees.

For those employees, generating a fresh annual entitlement through Pattern A during the middle of the same period can recreate leave that has already been consumed in the legacy system.

Instead, import the actual remaining balances as standalone Leave Allocations for the rest of the cutover period.

The key principle is:

> During a mid-period cutover, preserve the employee's real remaining balance rather than recreating the original annual entitlement.

### Pattern B is a transition pattern, not the normal long-term state

If the organization normally uses Leave Policies, imported standalone balances should usually be treated as a **one-time cutover bridge**.

At the start of the next normal Leave Period, continuing employees should normally move to Pattern A and receive their new-period entitlement through a Leave Policy Assignment.

For example, if:

```text
Frappe HR cutover:       18-Sep-2026
Current Leave Period:    01-Jan-2026 to 31-Dec-2026
Next Leave Period:       01-Jan-2027 to 31-Dec-2027
```

then a sensible implementation is:

```text
Existing employees at cutover
    Sep-Dec 2026
    → Pattern B: import verified remaining 2026 balances

New 2027 Leave Period
    01-Jan-2027
    → Pattern A: assign the 2027 Leave Policy
      to continuing employees
```

If the organization's Leave Period begins on another date, use that date instead of January 1.

This is a recommended migration pattern, not a universal Frappe HR rule. Organizations that intentionally use direct Leave Allocations, special employee-specific arrangements, or another entitlement process may choose differently.

### When Pattern B may not be necessary

Pattern B is not automatically required merely because an employee existed before go-live.

For example, if the implementation goes live exactly at the beginning of a new Leave Period and no legacy balance needs to be preserved, Pattern A may be appropriate immediately for existing employees as well.

---

## 16. Choose a cutover date

Define the date from which Frappe HR becomes authoritative for new leave transactions.

For example:

```text
ERP leave cutover date:       YYYY-MM-DD
Legacy balance date:          close of business on the prior day
```

The exact date and transition policy belong to the implementing organization.

---

## 17. Prepare verified opening balances

HR should provide an auditable opening-balance source.

Useful fields include:

| Column | Meaning |
|---|---|
| Employee ID | Frappe HR Employee ID |
| Employee Name | Human verification |
| Date of Joining | Actual historical Date of Joining |
| Company | Frappe Company |
| Balance As Of | Date to which the balance was reconciled |
| Leave Type balances | Remaining balance for each relevant Leave Type |
| Verified By | HR reviewer |
| Verification Date | Review date |
| Notes | Exceptions or reconciliation notes |

How future-dated approved or pending leave is handled is an organization-specific cutover decision and should be documented before import.

---

## 18. Prepare standalone Leave Allocation imports

Use Frappe's Data Import process for **Leave Allocation** when importing opening balances.

Typical fields may include:

| Column | Typical value |
|---|---|
| Employee | Frappe HR Employee ID |
| Company | Frappe Company |
| Leave Type | Exact configured Leave Type |
| From Date | Cutover/effective date |
| To Date | End of the applicable allocation period |
| Total Leaves Allocated | Verified opening balance |
| New Leaves Allocated | Verified opening balance |
| Description | Opening-balance / cutover note |

When importing standalone opening balances, Leave Policy, Leave Period, and Leave Policy Assignment are normally left unpopulated unless your migration design explicitly requires otherwise.

---

## 19. Import as Draft first

A safer migration sequence is:

- Import Type = Insert New Records;
- keep the uploaded file private;
- leave **Submit After Import** unchecked;
- suppress unnecessary emails if appropriate for your environment;
- review the preview;
- run the import;
- inspect the resulting Draft Leave Allocations.

### Verify drafts

For every imported allocation, verify:

- correct Employee;
- correct Leave Type;
- correct From Date;
- correct To Date;
- correct New Leaves Allocated;
- correct Total Leaves Allocated;
- Leave Policy Assignment is blank for a standalone opening-balance import;
- status = Draft.

Do not submit until the values have been checked.

---

## 20. Submit imported Leave Allocations

After validation, submit the imported Leave Allocations.

### Verify

Each intended allocation should show:

- status = Submitted;
- correct balance;
- correct validity dates;
- no Leave Policy Assignment linkage for a standalone opening balance unless your migration design intentionally requires one.

Then verify the employee's actual balance through Frappe HR and through the self-service UI.

---

# Part VI - End-to-end self-service verification

## 21. Verify employee leave balance

Log in as the employee.

Confirm that the self-service UI can load the employee's submitted Leave Allocations through:

```text
frappe_hr_self_service.employee_self_service.get_my_leave_balance
```

If no balance appears, use the troubleshooting section below.

---

## 22. Verify leave eligibility

Select a valid date range in the employee UI.

Confirm that the self-service layer can call:

```text
frappe_hr_self_service.employee_self_service.get_available_leave_types
```

and return the Leave Types permitted by the underlying Frappe HR state and any installed extension rules.

Organization-specific rules such as waiting periods, sequencing, or custom eligibility constraints belong outside the generic public app unless they are implemented through its documented extension points.

---

## 23. Verify leave request submission

Submit a test leave request through:

```text
frappe_hr_self_service.employee_self_service.create_leave_request
```

Confirm that:

- the Leave Application is created for the authenticated employee;
- the dates are correct;
- the Leave Type is correct;
- the expected approver is associated with the request;
- native Frappe HR validation is still enforced.

The browser should not be trusted to supply the employee identity.

---

## 24. Verify My Leave Requests

Confirm that the employee can retrieve their own requests using:

```text
frappe_hr_self_service.employee_self_service.get_my_leave_requests
```

The result should contain only Leave Applications belonging to the Employee derived from the current authenticated user.

---

## 25. Verify approver workflow

Complete one test request when practical:

1. employee submits the request;
2. approver sees the pending request;
3. approver reviews it;
4. approver approves or rejects it;
5. the resulting Leave Application state matches Frappe HR behavior;
6. after approval, the employee's leave balance reflects the approved leave.

This is the strongest proof that the employee, allocation, holiday, approval, and self-service configuration are working together.

---

# Part VII - Readiness checklist

## 26. Employee identity

- [ ] Employee exists
- [ ] Employee is Active
- [ ] Company is correct
- [ ] Date of Joining is correct
- [ ] User is linked
- [ ] exactly one active Employee is linked to the User
- [ ] User is enabled
- [ ] employee has the intended self-service access
- [ ] employee can reach the self-service home

## 27. Approval setup

- [ ] Leave Approver is set
- [ ] Leave Approver User exists and is enabled
- [ ] approver has the required approval permissions/role

## 28. Holiday setup

- [ ] Holiday List Assignment exists
- [ ] correct Holiday List is selected
- [ ] effective date is correct
- [ ] Holiday List Assignment is Submitted

## 29. Leave master setup

- [ ] required Leave Types exist
- [ ] Leave Type behavior matches approved policy
- [ ] carry-forward settings are correct
- [ ] waiting-period / working-day settings are correct where used
- [ ] earned-leave settings are correct where used
- [ ] Leave Period exists and has the correct dates, when used
- [ ] Leave Policy contains the correct Leave Types
- [ ] Annual Allocation values are correct
- [ ] Leave Policy is Submitted

## 30. Pattern A - policy-generated entitlement

When using Leave Policy Assignment:

- [ ] Leave Policy Assignment exists
- [ ] correct Leave Period/effective dates are selected
- [ ] correct policy is selected
- [ ] Leave Policy Assignment is Submitted
- [ ] expected Leave Allocations were generated
- [ ] generated Leave Allocations are Submitted
- [ ] earned-leave schedule is correct, where applicable

## 31. Pattern B - opening-balance cutover

When importing existing balances:

- [ ] Pattern B is being used for a deliberate cutover reason
- [ ] cutover/effective date is defined
- [ ] opening balances are verified by HR
- [ ] migration treatment of future approved/pending leave is documented
- [ ] standalone Leave Allocations were imported
- [ ] imported values were reviewed before submission
- [ ] imported allocations are Submitted
- [ ] no unintended duplicate entitlement exists for the same period
- [ ] transition to Pattern A at the next normal Leave Period has been planned, if the organization uses Leave Policies in steady state

## 32. End-to-end test

- [ ] self-service home opens
- [ ] balances are visible
- [ ] date selection successfully checks eligibility
- [ ] expected Leave Types are selectable
- [ ] employee can submit a request
- [ ] employee can view their own requests
- [ ] approver can see the request
- [ ] approver can approve/reject
- [ ] balance changes correctly after approval

---

# Part VIII - Troubleshooting

## 33. No leave balance is available

Check in this order:

1. Is the User linked to the correct Employee?
2. Is exactly one active Employee linked to that User?
3. Does the Employee have submitted Leave Allocations?
4. If using Pattern A, is the Leave Policy Submitted?
5. Is the Leave Policy Assignment Submitted rather than Draft?
6. Did submitting the Leave Policy Assignment generate the expected Leave Allocations?
7. Are those Leave Allocations Submitted?
8. Do their dates include the date being checked?
9. If this is Earned Leave, has the expected amount actually accrued yet?

A saved but Draft Leave Policy Assignment is a common reason expected allocations do not appear.

---

## 34. Balances display but leave eligibility fails

The balance endpoint may work even when Frappe HR cannot calculate leave days for a requested date range.

Check the Employee's Holiday List Assignment.

A typical failure is that no Holiday List can be resolved for the Employee and requested date.

Fix by verifying:

- the correct Holiday List Assignment exists;
- the date range covers the requested date;
- the assignment is Submitted.

---

## 35. Employee does not land on the self-service Workspace

Check the User's default Workspace or equivalent navigation configuration.

After saving, test using a new login or incognito session.

The exact Workspace name is organization-specific.

---

## 36. Employee request exists but balance did not reduce

Check:

- Leave Application status;
- whether the approver actually approved the request;
- whether the document reached the submitted/approved state expected by Frappe HR;
- allocation validity dates;
- any organization-specific leave policy rules.

An Open or Draft request is not equivalent to an approved/submitted leave transaction.

---

## 37. Imported employee has too much leave

Check whether both of these exist for the same period:

- imported opening Leave Allocations; and
- entitlement generated from a Leave Policy Assignment.

This can unintentionally duplicate entitlement.

Stop and review the migration design before processing further leave transactions.

---

## 38. Employee can see another employee's data

The browser should not send an Employee ID and have the server trust that value as the authority for self-service access.

The public self-service endpoints derive the Employee from the logged-in Frappe user.

If you create additional endpoints, follow the same pattern.

---

# Part IX - Administrative principles

## 39. Verify outcomes, not just configuration screens

Do not consider an employee fully configured merely because all setup forms contain values.

The final proof is:

1. correct balances in the employee self-service UI;
2. correct eligibility for selected dates;
3. successful employee request submission;
4. successful approver action;
5. correct post-approval balance;
6. employee can retrieve their own request history.

---

## 40. Keep policy separate from the reusable self-service layer

`frappe_hr_self_service` should remain reusable.

Examples of organization-specific behavior that should normally remain in a downstream app or operational configuration include:

- exact Leave Type configuration chosen by the organization;
- annual entitlement quantities;
- leave sequencing;
- waiting periods;
- entitlement formulas;
- proration rules;
- carry-forward policy;
- encashment policy;
- custom notifications;
- employee Workspace branding and routes;
- migration/cutover business decisions.

The administration guide documents **where** those decisions are configured in Frappe HR without prescribing what an organization's policy must be.

---

## 41. Keep UI configuration reproducible

If your self-service Workspace, Web Pages, Custom HTML Blocks, Custom Fields, or Email Templates are created only in the live database, they may not be reproducible on another site or after a rebuild.

Export organization-specific UI configuration as filtered fixtures from your own custom app.

See the [Employee Self-Service UI Starter Guide](EMPLOYEE_SELF_SERVICE_UI_STARTER_GUIDE.md) for a fixture example.

---

# Part X - Useful first automation

## 42. Leave setup readiness checker

Before automating document creation, a useful first automation is a read-only readiness checker that reports whether the employee is actually ready for self-service.

For example:

```text
✓ Active Employee
✓ Company configured
✓ User linked
✓ Exactly one active Employee linked to User
✓ Self-service access present
✓ Leave Approver configured
✓ Holiday List Assignment submitted
✓ Leave Types configured
✓ Leave Policy submitted
✓ Leave entitlement source configured
✓ Submitted Leave Allocations found

Overall: READY
```

or identifies exact failures such as:

```text
✗ Leave Policy Assignment is still Draft
✗ No submitted Leave Allocations found
✗ No applicable Holiday List Assignment found
```

A readiness checker is safer as a first automation because it makes configuration observable without making transactional decisions.

---

## 43. Later automation candidates

After the readiness checker is proven, an organization may automate selected administrative steps such as:

- setting the employee's self-service Workspace;
- creating Holiday List Assignments;
- assigning a submitted Leave Policy;
- creating Leave Policy Assignments;
- preparing opening-balance import rows;
- verifying generated or imported allocations;
- preparing the next-period transition from Pattern B to Pattern A.

Creation and submission of HR documents should remain explicit and auditable according to the organization's operating controls.

---

# 44. Final readiness summary

A working `frappe_hr_self_service` installation depends on a correctly configured Frappe HR foundation.

The normal steady-state chain is:

```text
Configured Leave Types
  ↓
Leave Period
  ↓
Submitted Leave Policy
  ↓
Active Employee
  ↓
Enabled User linked to that Employee
  ↓
Leave Approver configured
  ↓
Applicable Holiday List
  ↓
Submitted Leave Policy Assignment
  ↓
Submitted Leave Allocations
  ↓
Employee self-service request
  ↓
Approver action
  ↓
Frappe HR updates the authoritative leave state
```

During a mid-period implementation, existing employees may temporarily enter the process through Pattern B instead:

```text
Verified legacy remaining balances
  ↓
Standalone Leave Allocations for the cutover period
  ↓
Self-service operation
  ↓
Next normal Leave Period
  ↓
Pattern A, where Leave Policy Assignment is the organization's steady-state model
```

The public self-service app simplifies how employees and approvers interact with that state; it does not replace the underlying Frappe HR administration required to create it.